# 脚本文档链接：https://merico.feishu.cn/docx/AH1ldkU5eorb8oxPq4acOavFnxd
# 该脚本作用是获取项目列表-递归显示父项目和子项目
# 输入：暂不需要输入
# 输出：项目列表，包含每个项目的：项目ID、项目名称、项目描述、项目层级、项目架构、父项目ID、各级父项目信息、各级子项目信息

import sys
import os
from datetime import date, timedelta, datetime
sys.path.append("../..")
from open_api_client import Client
from open_api_sdk_v2 import get_all_group_id
from custom_sdk import get_group_list_dict, get_children_dict

endpoint = 'https://metrics.digitalvolvo.com/openapi'  # 填入您的思码逸系统完整域名和端口，注意最后不需要加 /
app_id = '8335655dae4bc4f9'  # 填入您的思码逸系统管理员账号openapi的app_id
secret = '06c31993a761e4a4d4831a860daf4460'  # 填入您的思码逸系统管理员账号openapi的secret

dt_now_start = datetime.now()
output_path = dt_now_start.strftime('04_output_project_list%Y%m%d%H%M%S/')
if not os.path.exists(output_path):
    os.makedirs(output_path)

dt_now_start = dt_now_start.isoformat("T")
date_year_ago = datetime.strftime(datetime.now() - timedelta(days=365), "%Y-%m-%d")
date_now = datetime.strftime(datetime.now(), "%Y-%m-%d")
date_now_total = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")

# 这个方法是获取所有项目列表list
def get_group_list(client):
    group_list = get_all_group_id(client)
    return group_list

# 这个方法是对group_list_dict的parent_dict字段进行一些优化显示
def get_parent_dict_detail(group_list_dict):
    parent_level_count = 0
    for index, i in enumerate(group_list_dict.items()):
        if len(i[1]['parent_dict']) > parent_level_count:
            parent_level_count = len(i[1]['parent_dict'])
    for index_2, i_2 in enumerate(group_list_dict.items()):
        for i_3 in range(parent_level_count):
            i_2[1][f'{i_3+1}级父项目ID'] = None
            i_2[1][f'{i_3+1}级父项目名称'] = None
    for index_4, i_4 in enumerate(group_list_dict.items()):
        for index_5, i_5 in enumerate(i_4[1]['parent_dict'].items()):
            i_4[1][f'{index_5+1}级父项目ID'] = i_5[1]['parent_id']
            i_4[1][f'{index_5+1}级父项目名称'] = i_5[1]['parent_name']
    for index_6, i_6 in enumerate(group_list_dict.items()):
        i_6[1]['项目层级'] = (len(i_6[1]['parent_dict']) + 1)
    for index_7, i_7 in enumerate(group_list_dict.items()):
        self_project_name = i_7[1]['name']
        project_structure_list = []
        for index_8, i_8 in enumerate(i_7[1]['parent_dict'].items()):
            project_structure_list.append(i_8[1]['parent_name'])
        project_structure_list.append(self_project_name)
        project_structure_list_string = ">".join(map(str, project_structure_list))
        i_7[1]['项目架构'] = project_structure_list_string
    group_list_dict = {k: v for k, v in sorted(group_list_dict.items(), key=lambda item:(item[1]["项目层级"], item[1]["项目架构"]), reverse=False)}
    print(f"恭喜成功导出项目列表: 项目数量 {len(group_list_dict)} ")
    return group_list_dict, parent_level_count

if __name__ == '__main__':
    dt_now_start = datetime.now()
    dt_now_start = dt_now_start.isoformat("T")
    date_now_total_ = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    client = Client(f'{endpoint}/openapi', app_id, secret)
    group_list = get_group_list(client)
    group_list_dict = get_group_list_dict(group_list)
    group_list_dict = get_children_dict(group_list_dict)
    group_list_dict, parent_level_count = get_parent_dict_detail(group_list_dict)

    # 打印所有项目关键信息
    headers = []
    headers.append('id')
    headers.append('name')
    headers.append('description')
    headers.append('项目层级')
    headers.append('项目架构')
    headers.append('parentId')
    headers.append('parent_dict')
    headers.append('children_dict')
    for i in range(parent_level_count):
        headers.append(f'{i+1}级父项目ID')
        headers.append(f'{i+1}级父项目名称')
    print(", ".join(headers))
    for v in group_list_dict.values():
        row = [str(v.get(h, '')) for h in headers]
        print(", ".join(row))

    dt_now_end = datetime.now()
    dt_now_end = dt_now_end.isoformat("T")
    print(f"打印输出完成, 开始时间{dt_now_start}")
    print(f"打印输出完成, 完成时间{dt_now_end}")




