# 脚本文档链接：https://merico.feishu.cn/docx/JtfHdizseoV4hrx8liCczoJonLf
# 该脚本作用是以团队聚合获取效率metric
# 输入：团队ID、团队名称，或者输入all，不支持不输入
# 输入：输入查询开始日期，若不输入则查询全量时间范围的效率数据
# 输入：输入查询结束日期，若不输入则查询全量时间范围的效率数据
# 输入：是否仅查询测试/非测试代码的当量 (此过滤条件仅支持开发当量，开发价值指标)，可以不输入或者输入true或者输入false:
# 输入：时间聚合范围：可以输入包括day、week、month、quarter、year，若不输入则使用week

import csv
import re
import sys
import os
import xlsxwriter
sys.path.append("../..")
from open_api_client import Client
from open_api_sdk_v2 import get_all_team_id, get_efficiency_metric_by_team_id
from custom_sdk import is_invalid_date, get_team_id_or_name_pattern, get_start_date_allow_empty, convert_list_to_dict, \
get_end_date_allow_empty, find_team_by_id_or_name, get_unit_of_time, get_test_code, write_worksheet, build_team_structure
from datetime import date, timedelta, datetime


file_name_date = datetime.now().strftime("%Y-%m-%d")
date_now_x = datetime.now().strftime("%H-%M-%S")
output_path = datetime.now().strftime('07_team_query_efficiency_metric_output%Y%m%d%H%M%S/')
if not os.path.exists(output_path):
    os.makedirs(output_path)

endpoint = 'https://metrics.digitalvolvo.com/openapi'  # 填入您的思码逸系统完整域名和端口，注意最后不需要加 /
app_id = '8335655dae4bc4f9'  # 填入您的思码逸系统管理员账号openapi的app_id
secret = '06c31993a761e4a4d4831a860daf4460'  # 填入您的思码逸系统管理员账号openapi的secret


chunk_size = 2 # 遍历数据时的数据规模，数据越大，每次请求数据时，传递的思码逸团队的ID就越多


filename_1 = f'{output_path}/02团队信息-{file_name_date}-{date_now_x}.csv'
filename_2 = f'{output_path}/01团队效率信息-{file_name_date}-{date_now_x}.csv'

workbook_1 = xlsxwriter.Workbook(filename_1)
workbook_2 = xlsxwriter.Workbook(filename_2)

workbook_1.set_tab_ratio(90) # 设置工作表选项卡和水平滑块之间的比率
workbook_2.set_tab_ratio(90) # 设置工作表选项卡和水平滑块之间的比率

worksheet_1 = workbook_1.add_worksheet('团队信息') # worksheet_1
worksheet_2 = workbook_2.add_worksheet('团队效率信息') # worksheet_2



def export_team_query_efficiency_metric(client, team_dict, start_date, end_date, unit_of_time, test_code):

    selectteamIds = [i for i in team_dict]

    # 需求1: 根据团队id，调用接口：以团队聚合获取效率metric
    team_query_efficiency_metrics_result = {}

    chunks = [selectteamIds[i:i+chunk_size] for i in range(0, len(selectteamIds), chunk_size)]
    # print(f"chunks = {chunks}")

    group_length = len(chunks)
    # print(f"group_length = {group_length}")


    team_exist = []
    for index, chunk in enumerate(chunks):
        chunk_team_id_list = chunk
        limit = len(chunk_team_id_list)

        chunk_team_name_list = [team_dict[id_]['name'] for id_ in chunk_team_id_list if id_ in team_dict]
        print(f"[{index+1}/{group_length}]当前进度为{round((index+1)/(group_length), 4)*100}%, 准备获取团队 {chunk_team_name_list} id = {chunk_team_id_list}的效率metric信息 ")
        team_query_efficiency_metrics = get_efficiency_metric_by_team_id(client, chunk_team_id_list, start_date, end_date, unit_of_time, test_code)
        team_query_efficiency_metrics = convert_list_to_dict(team_query_efficiency_metrics, 'teamId')
        # print(f"team_query_efficiency_metrics = {team_query_efficiency_metrics}")
        team_query_efficiency_metrics = {k: v for k, v in sorted(team_query_efficiency_metrics.items(), key=lambda item:(item[1]["teamId"], item[1]["date"]), reverse=False)}

        summary = 0
        for index, i in enumerate(team_query_efficiency_metrics.items()):
            # print(f"i = {i}")
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']] = {}
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['日期-时间范围-' + unit_of_time] = i[1]['date']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['团队ID'] = i[1]['teamId']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['团队名称'] = team_dict[i[1]['teamId']]['团队名称']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['新增代码当量'] = i[1]['dev_equivalent']

            # 下面这段代码作用是识别这个team是否已经出现过，如果出现过，就累加数据，求这个team的累积代码当量，如果没出现过，就重新计算。
            # print(f"team_exist = {team_exist}")
            if i[1]['teamId'] in team_exist:
                summary = summary + i[1]['dev_equivalent']
            else:
                summary = i[1]['dev_equivalent']
                team_exist.append(i[1]['teamId'])

            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['累积代码当量'] = summary
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['提交数'] = i[1]['commit_num']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['函数个数'] = i[1]['function_num']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['代码行数'] = i[1]['loc']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['新增代码行数'] = i[1]['loc_add_line']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['删除代码行数'] = i[1]['loc_delete_line']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['代码行数占比'] = i[1]['share_loc']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['开发者人数'] = i[1]['developer_num']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['开发价值'] = i[1]['dev_value']
            team_query_efficiency_metrics_result[str(index) + '-' + i[1]['teamId'] + '-' + i[1]['date']]['开发者平均开发当量'] = i[1]['dev_equivalent_every_developer']

        print(f"目前累计检索到的有当量新增的时间段数量是: {len(team_query_efficiency_metrics_result.keys())}")
        # print(f"team_exist = {team_exist}")

    return team_query_efficiency_metrics_result
   


if __name__ == '__main__':

    dt_now_start = datetime.now()
    dt_now_start = dt_now_start.isoformat("T")

    client = Client(f'{endpoint}/openapi', app_id, secret)

    # 输入team_id_pattern, 返回输入和regex
    special_team_id_regex, team_id_pattern = get_team_id_or_name_pattern()

    # 输入开始日期
    start_date = get_start_date_allow_empty(365)

    # 输入结束日期
    end_date = get_end_date_allow_empty()

    # 输入需要聚合的时间范围
    unit_of_time = get_unit_of_time('week')

    # 输入是否仅查询测试/非测试代码的当量 (此过滤条件仅支持开发当量，开发价值指标)
    test_code = get_test_code()

    team_list = get_all_team_id(client)
    team_dict, max_parent_hierarchy_length = build_team_structure(team_list)
    # 获取符合输入团队(组)ID 的 条件的团队(组)ID 的dict
    team_pattern_dict = find_team_by_id_or_name(special_team_id_regex, team_id_pattern, team_dict)

    # 导出团队信息为CSV
    if team_pattern_dict:
        headers = list(next(iter(team_pattern_dict.values())).keys())
        with open(filename_1, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, headers)
            writer.writeheader()
            writer.writerows(team_pattern_dict.values())

    # 导出team_query_efficiency_metric为CSV
    team_query_efficiency_metric = export_team_query_efficiency_metric(client, team_pattern_dict, start_date, end_date, unit_of_time, test_code)
    if team_query_efficiency_metric:
        headers2 = list(next(iter(team_query_efficiency_metric.values())).keys())
        with open(filename_2, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, headers2)
            writer.writeheader()
            writer.writerows(team_query_efficiency_metric.values())

    dt_now_end = datetime.now()
    dt_now_end = dt_now_end.isoformat("T")
    print(f"****执行结束****")
    print(f"\n")
    print(f"导出CSV完成, 开始时间{dt_now_start}")
    print(f"导出CSV完成, 完成时间{dt_now_end}")

    print(f"以下为本次检索条件: ")
    print(f"您输入的检索团队ID 或 团队名称 是(为all代表全部): {special_team_id_regex}")
    print(f"您输入的查询开始日期是(为空代表全部): {start_date}")
    print(f"您输入的查询结束日期是(为空代表全部): {end_date}")
    print(f"您输入的统计步长（需要聚合的时间范围），可以输入包括day、week、month、quarter、year: {unit_of_time}")
    print(f"您输入的是否仅查询测试/非测试代码的当量 (此过滤条件仅支持开发当量，开发价值指标)，可以不输入或者输入true或者输入false(为空代表全部): {test_code}")

