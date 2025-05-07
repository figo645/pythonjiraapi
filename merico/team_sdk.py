def get_all_team_id(client):
    resp = client.post("/team/list")
    if resp.get("code") != 200:
        raise Exception(f"API error: {resp}")
    return resp["data"]

def build_team_structure(team_list):
    team_dict = {team["id"]: team for team in team_list}
    def build_hierarchy(team_id, parent_chain):
        team = team_dict[team_id]
        team["parent_chain"] = parent_chain
        children = [t["id"] for t in team_list if t.get("parentId") == team_id]
        team["children"] = children
        for child_id in children:
            build_hierarchy(child_id, parent_chain + [team_id])
    roots = [t["id"] for t in team_list if not t.get("parentId")]
    for root_id in roots:
        build_hierarchy(root_id, [])
    return team_dict, max(len(t["parent_chain"]) for t in team_dict.values()) 