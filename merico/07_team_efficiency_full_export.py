import csv
import sys
import os
from datetime import datetime
sys.path.append("../..")
from open_api_client import Client
from open_api_sdk_v2 import get_all_team_id, get_efficiency_metric_by_team_id
from custom_sdk import (
    get_team_id_or_name_pattern, get_start_date_allow_empty, get_end_date_allow_empty,
    get_unit_of_time, get_test_code, build_team_structure, find_team_by_id_or_name, convert_list_to_dict
)

# 配置
endpoint = 'https://metrics.digitalvolvo.com/openapi'
app_id = '8335655dae4bc4f9'
secret = '06c31993a761e4a4d4831a860daf4460'

file_name_date = datetime.now().strftime("%Y-%m-%d")
date_now_x = datetime.now().strftime("%H-%M-%S")
output_path = datetime.now().strftime('07_team_efficiency_full_export_%Y%m%d%H%M%S/')
if not os.path.exists(output_path):
    os.makedirs(output_path)
filename = f'{output_path}/团队效率全量信息-{file_name_date}-{date_now_x}.csv'

if __name__ == '__main__':
    dt_now_start = datetime.now()
    dt_now_start = dt_now_start.isoformat("T")

    client = Client(f'{endpoint}/openapi', app_id, secret)

    # 1. 获取所有团队基础信息
    team_list = get_all_team_id(client)
    team_dict, _ = build_team_structure(team_list)

    # 2. 选择团队（可自定义为all或部分团队）
    special_team_id_regex, team_id_pattern = get_team_id_or_name_pattern()
    team_pattern_dict = find_team_by_id_or_name(special_team_id_regex, team_id_pattern, team_dict)

    # 3. 获取效率指标参数
    start_date = get_start_date_allow_empty(365)
    end_date = get_end_date_allow_empty()
    unit_of_time = get_unit_of_time('week')
    test_code = get_test_code()

    # 4. 获取所有团队效率指标
    all_team_ids = list(team_pattern_dict.keys())
    chunk_size = 2
    chunks = [all_team_ids[i:i+chunk_size] for i in range(0, len(all_team_ids), chunk_size)]
    efficiency_metrics = []
    for chunk in chunks:
        metrics = get_efficiency_metric_by_team_id(client, chunk, start_date, end_date, unit_of_time, test_code)
        efficiency_metrics.extend(metrics)

    # 5. 合并基础信息和效率指标
    eff_dict = {}
    for m in efficiency_metrics:
        key = (m['teamId'], m['date'])
        eff_dict[key] = m

    headers = ['团队ID', '团队名称', '父团队ID', '父链', '子团队数', '团队层级', '团队架构', '日期',
               '新增代码当量', '提交数', '函数个数', '代码行数', '新增代码行数', '删除代码行数', '代码行数占比', '开发者人数', '开发价值', '开发者平均开发当量']

    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for team_id, team in team_pattern_dict.items():
            for key, eff in eff_dict.items():
                if key[0] == team_id:
                    row = [
                        team_id,
                        team.get('name', ''),
                        team.get('parentId', ''),
                        '->'.join(team.get('parent_chain', [])),
                        len(team.get('children', [])),
                        len(team.get('parent_chain', [])),
                        team.get('团队架构', ''),
                        eff.get('date', ''),
                        eff.get('dev_equivalent', ''),
                        eff.get('commit_num', ''),
                        eff.get('function_num', ''),
                        eff.get('loc', ''),
                        eff.get('loc_add_line', ''),
                        eff.get('loc_delete_line', ''),
                        eff.get('share_loc', ''),
                        eff.get('developer_num', ''),
                        eff.get('dev_value', ''),
                        eff.get('dev_equivalent_every_developer', '')
                    ]
                    writer.writerow(row)

    dt_now_end = datetime.now()
    dt_now_end = dt_now_end.isoformat("T")
    print(f"导出CSV完成, 开始时间{dt_now_start}")
    print(f"导出CSV完成, 完成时间{dt_now_end}")
    print(f"输出文件: {filename}") 