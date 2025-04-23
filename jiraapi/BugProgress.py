import requests
import urllib.parse
import pandas as pd

# Jira API 相关信息
JIRA_URL = "https://jira.digitalvolvo.com"
API_TOKEN = "MDQ3NDAxMzQ2ODY0OiksiKm1bWeZ1sAfWgqRfQ2WrgPV"
JQL_QUERY = "issuetype in (故障) AND Sprint in openSprints()"
JQL_ENCODED = urllib.parse.quote(JQL_QUERY)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

# 分页获取所有 issue
all_issues = []
start_at = 0
max_results = 1000

while True:
    url = f"{JIRA_URL}/rest/api/2/search?jql={JQL_ENCODED}&startAt={start_at}&maxResults={max_results}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: API 请求失败，状态码 {response.status_code}")
        break

    data = response.json()
    issues = data.get("issues", [])
    all_issues.extend(issues)

    if len(issues) < max_results:
        break
    start_at += max_results

print(f"✅ 共获取到 {len(all_issues)} 条 issue")

# 处理数据
records = []

for issue in all_issues:
    fields = issue['fields']

    # 环境
    env_field = fields.get('customfield_10602')
    environment = env_field.get('value') if env_field else None
    priority = fields.get('priority', {}).get('name')  # 例如 "Medium: P2"

    # 获取级联字段
    team_field = fields.get('customfield_11101')
    parent_value = team_field.get('value') if team_field else None
    child_value = team_field.get('child', {}).get('value') if team_field and 'child' in team_field else None

    # 其他字段
    issue_key = issue['key']
    issue_type = fields.get('issuetype', {}).get('name')
    status = fields.get('status', {}).get('name')
    is_resolved = fields.get('resolution') is not None
    labels = fields.get('labels', [])
    has_change_label = any("变更" in label for label in labels)
    created = fields.get('created')

    # 记录
    records.append({
        "Issue Key": issue_key,
        "Issue Type": issue_type,
        "Status": status,
        "Resolved": is_resolved,
        "Priority": priority,
        "Environment": environment,
        "Team Parent": parent_value,
        "Team Child": child_value,
        "Created": created
    })
    print(records)

# 导出为 CSV
df = pd.DataFrame(records)
df.to_csv("jira_bug_export.csv", index=False, encoding='utf-8-sig')
print("✅ 已成功导出为 jira_bug_export.csv")