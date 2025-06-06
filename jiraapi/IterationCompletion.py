# 文件路径：/Users/xuchenfei/Documents/咨询/百度云同步盘/#网盘同步资料/聚科联诚Service Offering/DevFolder/pythonjiraapi/jiraapi/IterationCompletion.py

import requests
import urllib.parse
import pandas as pd
from datetime import datetime
import os
from jiraapi.BaseJira import BaseJira
from jiraapi.config import API_TOKEN, JIRA_EMAIL

class IterationCompletion(BaseJira):
    def __init__(self):
        super().__init__()
        self.API_TOKEN = API_TOKEN
        self.JIRA_EMAIL = JIRA_EMAIL
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        # Jira API 相关信息
        self.JIRA_URL = "https://jira.digitalvolvo.com"
        
        # 根据需求设置的JQL查询
        self.JQL_QUERY = "issuetype in (BA工作任务,任务, 技术需求Enabler, 故事, 测试QA工作任务, 运维任务) AND Sprint in openSprints()"
        #self.JQL_QUERY = "issuetype = 故事 AND Sprint = 1190 AND 交付团队 in cascadeOption(13004, 13100) and issuekey = \"CVTC-173020\""
        
        # 设置基础路径
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 输出文件路径
        self.OUTPUT_FILE = os.path.join(self.BASE_DIR, "data", "iteration_completion.csv")

    def get_jira_issues(self):
        """获取所有符合条件的JIRA问题"""
        all_issues = []
        start_at = 0
        max_results = 1000
        jql_encoded = urllib.parse.quote(self.JQL_QUERY)

        while True:
            url = f"{self.JIRA_URL}/rest/api/2/search?jql={jql_encoded}&startAt={start_at}&maxResults={max_results}"
            
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                issues = data.get("issues", [])
                
                if not issues:
                    break
                    
                all_issues.extend(issues)
                
                if len(issues) < max_results:
                    break
                    
                start_at += max_results
                
            except requests.exceptions.RequestException as e:
                print(f"Error: 获取JIRA数据失败: {str(e)}")
                break

        return all_issues

    def process_team_statistics(self, issues):
        """处理团队统计数据"""
        team_stats = {}

        for issue in issues:
            fields = issue['fields']
            
            # 获取交付团队信息
            team_field = fields.get('customfield_11101')
            program_name = team_field.get('value') if team_field else "Unassigned Program"
            team_name = team_field.get('child', {}).get('value') if team_field and 'child' in team_field else "Unassigned Team"
            
            # 获取故事点
            story_points = fields.get('customfield_10002', 0) or 0
            
            # 初始化团队数据
            if team_name not in team_stats:
                team_stats[team_name] = {
                    "programName": program_name,
                    "plannedCount": 0,
                    "completedCount": 0,
                    "storypointPlanned": 0,
                    "storypointCompleted": 0
                }
            
            # 更新计划数量和计划story points
            team_stats[team_name]["plannedCount"] += 1
            team_stats[team_name]["storypointPlanned"] += story_points
            
            # 更新完成数量和完成story points
            if fields.get('resolution') is not None:
                team_stats[team_name]["completedCount"] += 1
                team_stats[team_name]["storypointCompleted"] += story_points

        return team_stats

    def generate_report(self):
        """生成迭代完成情况报告"""
        print("开始获取JIRA数据...")
        issues = self.get_jira_issues()
        print(f"✅ 共获取到 {len(issues)} 条issue")

        if not issues:
            print("Warning: 未获取到任何issue数据")
            return

        # 处理统计数据
        team_stats = self.process_team_statistics(issues)

        # 转换为DataFrame格式
        records = []
        for team, stats in team_stats.items():
            records.append({
                "programName": stats["programName"],
                "teamName": team,
                "plannedProgress": stats["plannedCount"],
                "actualProgress": stats["completedCount"],
                "storypointPlanned": round(stats["storypointPlanned"], 2),
                "storypointCompleted": round(stats["storypointCompleted"], 2)
            })

        # 创建DataFrame
        df = pd.DataFrame(records)

        # 设置浮点数显示格式
        float_columns = ['storypointPlanned', 'storypointCompleted']
        for col in float_columns:
            df[col] = df[col].round(2)

        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(self.OUTPUT_FILE), exist_ok=True)
            
            # 保存到CSV文件，设置浮点数格式
            df.to_csv(self.OUTPUT_FILE, index=False, encoding='utf-8-sig', float_format='%.2f')
            print(f"✅ 已成功导出迭代完成情况统计到: {self.OUTPUT_FILE}")
            
            # 打印统计结果
            pd.set_option('display.float_format', '{:.2f}'.format)
            print("\n迭代完成情况统计：")
            print(df.to_string(index=False))
            
        except Exception as e:
            print(f"Error: 保存CSV文件失败: {str(e)}")

def main():
    """主函数"""
    try:
        iteration_completion = IterationCompletion()
        iteration_completion.generate_report()
    except Exception as e:
        print(f"Error: 程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()