import requests
import pandas as pd
import os
from datetime import datetime


class TestCasesAnalyzer:
    def __init__(self):
        self.JIRA_URL = "https://jira.digitalvolvo.com"
        self.API_TOKEN = "MDQ3NDAxMzQ2ODY0OiksiKm1bWeZ1sAfWgqRfQ2WrgPV"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        # 设置输出目录
        self.OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        # 设置测试计划key
        self.TEST_PLAN_KEY = "CVTC-172997"

    def get_test_cycles(self):
        """获取测试计划的所有测试周期"""
        try:
            url = f"{self.JIRA_URL}/rest/synapse/latest/public/testPlan/{self.TEST_PLAN_KEY}/cycles"
            print(f"\n正在获取测试计划 {self.TEST_PLAN_KEY} 的测试周期...")
            print(f"请求URL: {url}")

            response = requests.get(url, headers=self.headers)
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")  # 打印前500个字符

            if response.status_code != 200:
                print(f"获取测试周期失败，状态码: {response.status_code}")
                return []

            return response.json()
        except Exception as e:
            print(f"获取测试周期时发生错误: {str(e)}")
            return []

    def get_test_cases(self):
        """获取测试计划中的所有测试用例"""
        try:
            url = f"{self.JIRA_URL}/rest/synapse/latest/public/testPlan/{self.TEST_PLAN_KEY}/members"
            print(f"\n正在获取测试计划 {self.TEST_PLAN_KEY} 的测试用例...")
            print(f"请求URL: {url}")

            response = requests.get(url, headers=self.headers)
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text[:500]}")  # 打印前500个字符

            if response.status_code != 200:
                print(f"获取测试用例失败，状态码: {response.status_code}")
                return []

            return response.json()
        except Exception as e:
            print(f"获取测试用例时发生错误: {str(e)}")
            return []

    def analyze_test_cases(self):
        """分析测试用例的状态"""
        try:
            # 获取测试周期
            test_cycles = self.get_test_cycles()
            if not test_cycles:
                print("未找到测试周期")
                return None

            # 获取测试用例
            test_cases = self.get_test_cases()
            if not test_cases:
                print("未找到测试用例")
                return None

            # 初始化统计
            statistics = {
                'total_cases': len(test_cases),
                'passed_cases': 0,
                'failed_cases': 0,
                'blocked_cases': 0,
                'not_run_cases': 0,
                'case_details': []
            }

            # 分析每个测试用例
            for test_case in test_cases:
                case_id = test_case.get('id')
                print(f"\n分析测试用例: {case_id}")

                # 获取执行状态
                status = test_case.get('status', '')

                # 更新统计
                if status == '通过' or status == 'Approved':
                    statistics['passed_cases'] += 1
                elif status == '失败' or status == 'Failed':
                    statistics['failed_cases'] += 1
                elif status == '阻塞' or status == 'Blocked':
                    statistics['blocked_cases'] += 1
                else:
                    statistics['not_run_cases'] += 1

                # 记录详细信息
                statistics['case_details'].append({
                    'id': case_id,
                    'name': test_case.get('name', ''),
                    'description': test_case.get('description', ''),
                    'status': status,
                    'priority': test_case.get('priority', ''),
                    'component': test_case.get('component', '')
                })

            return statistics
        except Exception as e:
            print(f"分析测试用例时发生错误: {str(e)}")
            return None

    def export_to_csv(self, statistics):
        """导出分析结果到CSV文件"""
        try:
            # 确保输出目录存在
            os.makedirs(self.OUTPUT_DIR, exist_ok=True)

            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'test_cases_analysis_{self.TEST_PLAN_KEY}_{timestamp}.csv'

            # 创建DataFrame
            df = pd.DataFrame([{
                'test_plan_key': self.TEST_PLAN_KEY,
                'total_cases': statistics['total_cases'],
                'passed_cases': statistics['passed_cases'],
                'failed_cases': statistics['failed_cases'],
                'blocked_cases': statistics['blocked_cases'],
                'not_run_cases': statistics['not_run_cases'],
                'pass_rate': round((statistics['passed_cases'] / statistics['total_cases'] * 100)
                                   if statistics['total_cases'] > 0 else 0, 2)
            }])

            # 导出到CSV
            output_file = os.path.join(self.OUTPUT_DIR, filename)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ 已成功导出分析结果到: {output_file}")

            # 打印统计结果
            print("\n测试用例分析统计：")
            print(df.to_string(index=False))

            # 打印详细信息
            print("\n测试用例详细信息：")
            for case in statistics['case_details']:
                print(f"\n测试用例ID: {case['id']}")
                print(f"名称: {case['name']}")
                print(f"描述: {case['description']}")
                print(f"状态: {case['status']}")
                print(f"优先级: {case['priority']}")
                print(f"组件: {case['component']}")

        except Exception as e:
            print(f"❌ 导出分析结果时发生错误: {str(e)}")

    def run_analysis(self):
        """运行分析流程"""
        print(f"\n开始分析测试计划: {self.TEST_PLAN_KEY}")

        # 分析测试用例
        statistics = self.analyze_test_cases()
        if statistics:
            # 导出结果
            self.export_to_csv(statistics)
        else:
            print("❌ 分析失败，请检查日志")


if __name__ == "__main__":
    # 运行分析
    analyzer = TestCasesAnalyzer()
    analyzer.run_analysis()