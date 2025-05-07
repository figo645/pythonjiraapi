# 脚本文档链接：https://merico.feishu.cn/docx/XdPedg406oKqAoxEC4ecX3HZnBg
# （一）原始需求
# 该脚本作用是查询迭代表现项目千当量缺陷率指标趋势
# 输入1：项目ID 或 项目名称(支持正则匹配，间隔符号仅支持英文|) 或 all(代表查询全部项目的项目成员)，不支持输入为空
# 输入2：确认需要使用哪种项目统计模式：仅子节点(child nodes only)或者全部后代节点(all descendant nodes)，输入1或者2进行选择，若不输入，则默认使用仅子节点模式
# 输入3：回溯时间参数中的时间量词("day" "week" "month" "quarter" "year")，支持输入为空，也就是不输入
# 输入4：回溯时间参数中的时间量值(正整数)，支持输入为空，也就是不输入
# 输入3和输入4，两个必须同时为有效参数，才会将回溯时间参数生效，否则当他们有1个或2个都为空时，会认为是输入为空
# 输入5：起始日期，输入想要查询同行数据的起始日期，格式为xxxx-xx-xx，支持输入为空
# 输入6：结束日期，输入想要查询同行数据的结束日期，格式为xxxx-xx-xx，支持输入为空
# 输入5和输入6，两个必须同时为有效参数，才会将起始日期和结束日期参数生效，否则当他们有1个或2个都为空时，会认为是输入为空
# 当输入5输入为空时，使用默认起始日期，具体为脚本执行当天3个月之前的日期
# 当输入6输入为空时，使用默认结束日期，具体为脚本执行当天日期
# 有关输入3和4、输入5和6的备注，如果输入3和4、输入5和6同时存在且有效，只取输入3和4的数据，忽略输入5和6
# 也就是当dateQuery参数中，同时传递recentPeriod和dateRange参数时，接口会取recentPeriod 中的值进行真正的传参，而忽略dateRange中的参数
# 输入7：分组维度，支持输入 "sprint" "week" "month"，若不输入，则使用sprint

# 输出：返回指定 项目 或 全部项目 的迭代表现项目千当量缺陷率指标趋势（具体字段参见 openapi IssueTracking查询迭代表现项目千当量缺陷率指标趋势接口说明）



import csv
import re
import sys
import os
import string
import random
import xlsxwriter
sys.path.append("../..")
from open_api_client import Client
from open_api_sdk_v2 import get_all_group_id, get_all_repo_id, get_industry_dev_eq_per_capita, get_list_project_by_group_id, get_project_bug_per_k_dev_eq_trending
from datetime import date, timedelta, datetime
from custom_sdk import get_project_statistical_mode, get_project_id_or_name_pattern, \
get_group_list_dict, get_children_dict, write_worksheet, get_recentPeriod_counts,find_project_by_id_or_name, \
get_recentPeriod_unit, get_since, get_parent_dict_detail, get_execution_mode, chunk_dict, build_project_structure, \
get_start_date_allow_empty, get_end_date_allow_empty, get_groupDimension,\
convert_list_to_dict_without_random_str, get_project_statistical_dict, update_dict_from_another,\
find_repo_by_id_or_name, unify_keys_in_nested_dicts


file_name_date = datetime.now().strftime("%Y-%m-%d")
date_now_x = datetime.now().strftime("%H-%M-%S")
output_path = os.path.join('data')
if not os.path.exists(output_path):
    os.makedirs(output_path)


endpoint = 'https://metrics.digitalvolvo.com/openapi'  # 填入您的思码逸系统完整域名和端口，注意最后不需要加 /
app_id = '8335655dae4bc4f9'  # 填入您的思码逸系统管理员账号openapi的app_id
secret = '06c31993a761e4a4d4831a860daf4460'  # 填入您的思码逸系统管理员账号openapi的secret



filename_1 = os.path.join(output_path, '03项目(组)信息.csv')
filename_2 = os.path.join(output_path, '02迭代表现项目无数据信息.csv')
filename_3 = os.path.join(output_path, '01迭代表现项目千当量缺陷率指标趋势信息.csv')

workbook_1 = xlsxwriter.Workbook(filename_1)
workbook_2 = xlsxwriter.Workbook(filename_2)
workbook_3 = xlsxwriter.Workbook(filename_3)

workbook_1.set_tab_ratio(90) # 设置工作表选项卡和水平滑块之间的比率
workbook_2.set_tab_ratio(90) # 设置工作表选项卡和水平滑块之间的比率
workbook_3.set_tab_ratio(90) # 设置工作表选项卡和水平滑块之间的比率

worksheet_1 = workbook_1.add_worksheet('项目(组)') # worksheet_1
worksheet_2 = workbook_2.add_worksheet('迭代表现项目无数据项目') # worksheet_2
worksheet_3 = workbook_3.add_worksheet('迭代表现项目千当量缺陷率指标趋势信息') # worksheet_3


def get_result(client, all_project_count, project_statistical_dict, recentPeriod_counts, recentPeriod_unit, start_date, end_date, groupDimension):
    result_dict = {}
    result_dict_with_have = {}
    result_dict_with_no = {}
    project_id_list = [v['id'] for v in project_statistical_dict.values()]
    project_name_list = [v['name'] for v in project_statistical_dict.values()]
    if len(project_statistical_dict) == all_project_count:
        projectIds = None
    else:
        projectIds = project_id_list
    code, message, result = get_project_bug_per_k_dev_eq_trending(client, projectIds, recentPeriod_counts, recentPeriod_unit, start_date, end_date, groupDimension)

    print("DEBUG result type:", type(result))
    print("DEBUG result sample:", str(result)[:500])

    if isinstance(result, dict):
        iterable = result.values()
    else:
        iterable = result

    for i in iterable:
        if not isinstance(i, dict):
            print("WARNING: 非法数据项，已跳过：", i)
            continue
        result_dict['projectId'] = {}
        result_dict['projectId']['projectId'] = i.get('projectId', '')
        result_dict['projectId']['projectName'] = project_statistical_dict.get(i.get('projectId', ''), {}).get('name', '')
        if i.get('series'):
            for i_2 in i['series']:
                ran_str = ''.join(random.sample(string.ascii_letters + string.digits, 20))
                merged_dict = i_2.copy()
                merged_dict['project_id'] = i.get('projectId', '')
                merged_dict['project_name'] = project_statistical_dict.get(i.get('projectId', ''), {}).get('name', '')
                i_3 = merged_dict
                result_dict_with_have.update({f"{ran_str}" : i_3})
        else:
            result_dict_with_no.update(result_dict)

    return result_dict_with_no, result_dict_with_have



if __name__ == '__main__':
    dt_now_start = datetime.now()
    dt_now_start = dt_now_start.isoformat("T")
    client = Client(f'{endpoint}/openapi', app_id, secret)


    # 输入project_id_pattern, 返回输入和regex
    special_project_id_regex, project_id_pattern = get_project_id_or_name_pattern()


    # 输入使用哪种项目统计模式, 返回输入和模式: child nodes only 或者 all descendant nodes
    special_project_statistical_mode_number, special_project_statistical_mode = get_project_statistical_mode()


    # 非必填, recentPeriod输入时间周期数量
    recentPeriod_counts = get_recentPeriod_counts()

    # 非必填, recentPeriod输入时间周期单位
    recentPeriod_unit = get_recentPeriod_unit()

    # 输入4和输入5，两个必须同时为有效参数，才会将回溯时间参数生效，否则当他们有1个或2个都为空时，会认为是输入为空
    if (not recentPeriod_counts) or (not recentPeriod_unit):
        recentPeriod_counts = ''
        recentPeriod_unit = ''


    # 非必填, 输入开始日期
    start_date = get_start_date_allow_empty(90)


    # 非必填, 输入结束日期
    end_date = get_end_date_allow_empty()

    # 输入7：分组维度，支持输入 "sprint" "week" "month"，若不输入，则使用sprint
    groupDimension = get_groupDimension('sprint')


    # 输入6和输入7，两个必须同时为有效参数，才会将起始日期和结束日期参数生效，否则当他们有1个或2个都为空时，会认为是输入为空
    # 当输入6输入为空时，使用默认起始日期，具体为脚本执行当天3个月之前的日期
    # 当输入7输入为空时，使用默认结束日期，具体为脚本执行当天日期
    if (not start_date) or (not end_date):
        start_date = datetime.strftime(datetime.now() - timedelta(days=90), "%Y-%m-%d")
        end_date = datetime.strftime(datetime.now(), "%Y-%m-%d")
        print(f"由于起始日期 和结束日期，有空的情况，因此使用默认起始日期，具体为脚本执行当天3个月之前的日期 {start_date}, 使用默认结束日期，具体为当天 {end_date}")



    # 获取所有项目
    group_list = get_all_group_id(client)
    group_list_dict, max_parent_hierarchy_length = build_project_structure(group_list)
    all_project_count = len(group_list_dict)



    # 获取符合输入项目(组)ID 的 条件的项目(组)ID 的dict
    project_pattern_dict = find_project_by_id_or_name(special_project_id_regex, project_id_pattern, group_list_dict)


    # 获取符合项目统计模式 仅子节点(child nodes only)或者全部后代节点(all descendant nodes) 的项目(组)ID 的dict
    project_statistical_dict = get_project_statistical_dict(special_project_statistical_mode, project_pattern_dict)
    project_statistical_dict = update_dict_from_another(project_statistical_dict, group_list_dict)
    project_statistical_dict = {k: v for k, v in sorted(project_statistical_dict.items(), key=lambda item:(item[1]["project_level"], item[1]["project_hierarchy"]), reverse=False)}
    project_statistical_dict = unify_keys_in_nested_dicts(project_statistical_dict)
    # 输出项目(组)信息为CSV
    if project_statistical_dict:
        headers1 = list(next(iter(project_statistical_dict.values())).keys())
        with open(filename_1, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, headers1)
            writer.writeheader()
            writer.writerows(project_statistical_dict.values())



    result_dict_with_no, result_dict_with_have = get_result(client, all_project_count, project_statistical_dict, recentPeriod_counts, recentPeriod_unit, start_date, end_date, groupDimension)
    # 输出无数据信息为CSV
    if result_dict_with_no:
        headers2 = list(next(iter(result_dict_with_no.values())).keys())
        with open(filename_2, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, headers2)
            writer.writeheader()
            writer.writerows(result_dict_with_no.values())
    # 输出千当量缺陷率指标趋势信息为CSV
    if result_dict_with_have:
        # 自动合并所有key，确保所有字段都写入
        all_keys = set()
        for v in result_dict_with_have.values():
            all_keys.update(v.keys())
        headers3 = list(all_keys)
        with open(filename_3, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, headers3)
            writer.writeheader()
            writer.writerows(result_dict_with_have.values())



    dt_now_end = datetime.now()
    dt_now_end = dt_now_end.isoformat("T")
    print(f"****执行结束****")
    print(f"\n")
    print(f"导出CSV完成, 开始时间{dt_now_start}")
    print(f"导出CSV完成, 完成时间{dt_now_end}")
    print(f"以下为本次检索条件: ")
    print(f"您输入的检索项目ID 或 项目名称 是(为all代表全部): {special_project_id_regex}")
    print(f"您使用的项目统计模式是: {special_project_statistical_mode}")
    print(f"您输入的检索recentPeriod输入时间周期数量: {recentPeriod_counts}")
    print(f"您输入的检索recentPeriod输入时间周期单位: {recentPeriod_unit}")
    print(f"您输入的开始日期start_date: {start_date}")
    print(f"您输入的结束日期end_date: {end_date}")
    print(f"您输入的分组维度groupDimension: {groupDimension}")

