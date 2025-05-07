# 脚本文档链接：https://merico.feishu.cn/docx/D8CmdyGTMotMZKxomoHctwKpnwf
# 该脚本作用是获取团队列表-递归显示父团队和子团队
# 团队列表， 本方法需要登录账户拥有至少以下一个workspace的权限: [system-config -> members，system-config -> group，system-config -> squad]，对应设置中的团队管理权限
# 输入：暂不需要输入
# 输出：团队列表，包含每个团队的：团队ID、团队名称、团队层级、团队架构、父团队ID、各级父团队信息、各级子团队信息


import sys
import os
from datetime import datetime
sys.path.append("../..")
from merico_client import Client
from team_sdk import get_all_team_id, build_team_structure

file_name_date = datetime.now().strftime("%Y-%m-%d")
date_now_x = datetime.now().strftime("%H-%M-%S")
output_path = datetime.now().strftime('04_team_list_output%Y%m%d%H%M%S/')
if not os.path.exists(output_path):
    os.makedirs(output_path)

endpoint = 'https://metrics.digitalvolvo.com/openapi'  # 填入您的思码逸系统完整域名和端口，注意最后不需要加 /
app_id = '8335655dae4bc4f9'  # 填入您的思码逸系统管理员账号openapi的app_id
secret = '06c31993a761e4a4d4831a860daf4460'  # 填入您的思码逸系统管理员账号openapi的secret

# 这个方法是获取所有团队列表list
def get_team_list(client):
    team_list = get_all_team_id(client)
    return team_list

if __name__ == '__main__':
    dt_now_start = datetime.now()
    dt_now_start = dt_now_start.isoformat("T")
    date_now_total_ = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    client = Client(endpoint, app_id, secret)
    team_list = get_all_team_id(client)
    team_dict, max_parent_hierarchy_length = build_team_structure(team_list)
    print(f"恭喜成功导出团队列表: 团队数量 {len(team_dict)} ")

    print("团队ID, 团队名称, 父团队ID, 层级, 父链, 子团队数")
    for team in team_dict.values():
        print(
            f"{team['id']}, {team.get('name', '')}, {team.get('parentId', '')}, "
            f"{len(team['parent_chain'])}, {'->'.join(team['parent_chain'])}, {len(team['children'])}"
        )

    dt_now_end = datetime.now()
    dt_now_end = dt_now_end.isoformat("T")
    print(f"****执行结束****")
    print(f"\n")
    print(f"打印输出完成, 开始时间{dt_now_start}")
    print(f"打印输出完成, 完成时间{dt_now_end}")

