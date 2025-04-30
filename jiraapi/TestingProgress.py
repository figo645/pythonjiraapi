import requests
import urllib.parse
import pandas as pd
import os
from datetime import datetime
from jiraapi.BaseJira import BaseJira
from jiraapi.config import API_TOKEN, JIRA_EMAIL

class TestingProgress(BaseJira):
    def __init__(self):
        super().__init__()
        self.API_TOKEN = API_TOKEN
        self.JIRA_EMAIL = JIRA_EMAIL
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        # 修改为获取测试计划的JQL
        self.JQL_QUERY = 'issuetype = "测试计划" AND Sprint in openSprints()'
        # 设置输出目录为上一层的data
        self.OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        # 设置测试计划key
        self.TEST_PLAN_KEY = "CVTC-172997"

    def get_jira_data(self):
        """获取JIRA数据"""
        try:
            # 对JQL查询进行URL编码
            encoded_jql = urllib.parse.quote(self.JQL_QUERY)
            url = f"https://jira.digitalvolvo.com/rest/api/2/search?jql={encoded_jql}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            return response.json()['issues']
            
        except Exception as e:
            print(f"获取JIRA数据时发生错误: {str(e)}")
            return []

    def process_data(self):
        """处理数据并返回DataFrame"""
        # 获取测试计划数据
        test_plans = self.get_jira_data()
        
        # 初始化数据列表
        data = []
        
        print(f"\n✅ 共获取到 {len(test_plans)} 条测试计划")
        
        # 处理每个测试计划
        for test_plan in test_plans:
            fields = test_plan['fields']
            
            # 获取团队信息
            team_field = fields.get('customfield_11101', {})
            team_name = (team_field.get('child', {}).get('value', 'Unassigned Team') 
                        if team_field and 'child' in team_field 
                        else "Unassigned Team")
            
            # 获取测试计划状态
            status = fields.get('status', {}).get('name', 'Unknown')
            
            # 将数据添加到列表中
            data.append({
                'team': team_name,
                'status': status
            })
        
        # 创建DataFrame
        df = pd.DataFrame(data)
        
        # 按团队分组并计算统计数据
        stats = df.groupby('team').agg({
            'status': [
                'count',  # 总数
                lambda x: sum(x == 'DONE'),  # 完成数
                lambda x: sum(x == 'Failed'),  # 失败数
                lambda x: sum(x == 'Blocked')  # 阻塞数
            ]
        }).reset_index()
        
        # 重命名列
        stats.columns = ['teamName', 'totalTestCases', 'completedTestCases', 'failedTestCases', 'blockedTestCases']
        
        return stats

    def export_to_csv(self, df, filename='testing_progress.csv'):
        """导出DataFrame到CSV文件"""
        try:
            # 确保输出目录存在
            os.makedirs(self.OUTPUT_DIR, exist_ok=True)
            
            # 导出到CSV
            output_file = os.path.join(self.OUTPUT_DIR, filename)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ 已成功导出测试进展统计到: {output_file}")
            
            # 打印统计结果
            print("\n测试进展统计：")
            print(df.to_string(index=False))
            
        except Exception as e:
            print(f"❌ 导出统计数据时发生错误: {str(e)}")

    def run(self):
        """运行统计流程"""
        # 处理数据
        stats_df = self.process_data()
        
        # 导出到CSV
        self.export_to_csv(stats_df)

if __name__ == "__main__":
    progress = TestingProgress()
    progress.run()