# 文件路径：/Users/xuchenfei/Documents/咨询/百度云同步盘/#网盘同步资料/聚科联诚Service Offering/DevFolder/pythonjiraapi/jiraapi/IterationCompletion.py

import requests
import urllib.parse
import pandas as pd
from datetime import datetime
import os
import numpy as np


class SprintPlanning:
    def __init__(self):
        # Jira API 相关信息
        self.JIRA_URL = "https://jira.digitalvolvo.com"
        self.API_TOKEN = "MDQ3NDAxMzQ2ODY0OiksiKm1bWeZ1sAfWgqRfQ2WrgPV"

        # 根据需求设置的JQL查询
        self.JQL_QUERY = "issuetype in (BA工作任务,任务, 技术需求Enabler, 故事, 测试QA工作任务, 运维任务) AND Sprint in openSprints()"
        # self.JQL_QUERY = "issuetype = 故事 AND Sprint = 1190 AND 交付团队 in cascadeOption(13004, 13100) and issuekey = \"CVTC-173020\""

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_TOKEN}"
        }

        # 设置基础路径
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 输出文件路径
        self.OUTPUT_FILE = os.path.join(self.BASE_DIR, "data", "sprint_planning.csv")

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
            team_name = team_field.get('child', {}).get(
                'value') if team_field and 'child' in team_field else "Unassigned Team"

            # 获取各种故事点
            story_points = fields.get('customfield_10106', 0) or 0  # 普通故事点
            test_points = fields.get('customfield_10501', 0) or 0  # 测试故事点
            user_story_points = fields.get('customfield_10106', 0) or 0  # 用户故事点数
            issue_type = fields.get('issuetype', {}).get('name', '')

            # 初始化团队数据
            if team_name not in team_stats:
                team_stats[team_name] = {
                    "programName": program_name,
                    "plannedCount": 0,
                    "completedCount": 0,
                    "storypointPlanned": 0,
                    "storypointCompleted": 0,
                    "testPoints": 0,
                    "userStoryPoints": 0,
                    "enablerPoints": 0,
                    "totalPoints": 0,
                    "userStoryCount": 0,  # 新增：用户故事数量
                    "totalUserStoryPoints": 0,  # 新增：用户故事总点数
                    "storyPointsList": []  # 新增：存储所有故事的故事点数
                }

            # 更新计划数量和计划story points
            team_stats[team_name]["plannedCount"] += 1
            team_stats[team_name]["storypointPlanned"] += story_points
            team_stats[team_name]["testPoints"] += test_points
            team_stats[team_name]["totalPoints"] += story_points

            # 更新用户故事点数和技术需求点数
            if issue_type == "故事":
                team_stats[team_name]["userStoryPoints"] += user_story_points
                team_stats[team_name]["userStoryCount"] += 1  # 增加用户故事计数
                team_stats[team_name]["totalUserStoryPoints"] += user_story_points  # 累加用户故事点数
                team_stats[team_name]["storyPointsList"].append(user_story_points)  # 新增：记录故事点数
            elif issue_type == "技术需求Enabler":
                team_stats[team_name]["enablerPoints"] += story_points

            # 更新完成数量和完成story points
            if fields.get('resolution') is not None:
                team_stats[team_name]["completedCount"] += 1
                team_stats[team_name]["storypointCompleted"] += story_points

        return team_stats

    def generate_report(self):
        """生成迭代规划报告"""
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
            # 计算占比
            total_points = stats["totalPoints"]
            user_story_ratio = (stats["userStoryPoints"] / total_points * 100) if total_points > 0 else 0
            enabler_ratio = (stats["enablerPoints"] / total_points * 100) if total_points > 0 else 0
            
            # 计算需求吞吐量
            story_throughput = (stats["userStoryCount"] / stats["totalUserStoryPoints"] * 100) if stats["totalUserStoryPoints"] > 0 else 0
            
            # 计算CV值（变异系数）
            story_points_list = stats["storyPointsList"]
            cv_value = 0
            if len(story_points_list) > 0:
                mean = np.mean(story_points_list)
                std = np.std(story_points_list)
                cv_value = (std / mean * 100) if mean > 0 else 0
            
            # 计算需求颗粒度
            story_granularity = (stats["userStoryPoints"] / stats["userStoryCount"]) if stats["userStoryCount"] > 0 else 0
            
            records.append({
                "programName": stats["programName"],
                "teamName": team,
                "plannedProgress": stats["plannedCount"],
                "actualProgress": stats["completedCount"],
                "storypointPlanned": round(stats["storypointPlanned"], 2),
                "storypointCompleted": round(stats["storypointCompleted"], 2),
                "testPoints": round(stats["testPoints"], 2),
                "userStoryPoints": round(stats["userStoryPoints"], 2),
                "userStoryRatio": round(user_story_ratio, 2),
                "enablerPoints": round(stats["enablerPoints"], 2),
                "enablerRatio": round(enabler_ratio, 2),
                "storyThroughput": round(story_throughput, 2),
                "cvValue": round(cv_value, 2),  # 新增：CV值
                "storyGranularity": round(story_granularity, 2)  # 新增：需求颗粒度
            })

        # 创建DataFrame
        df = pd.DataFrame(records)

        # 设置浮点数显示格式
        float_columns = [
            'storypointPlanned', 'storypointCompleted', 'testPoints', 
            'userStoryPoints', 'userStoryRatio', 'enablerPoints', 
            'enablerRatio', 'storyThroughput', 'cvValue', 'storyGranularity'
        ]
        for col in float_columns:
            df[col] = df[col].round(2)

        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(self.OUTPUT_FILE), exist_ok=True)
            
            # 保存到CSV文件，设置浮点数格式
            df.to_csv(self.OUTPUT_FILE, index=False, encoding='utf-8-sig', float_format='%.2f')
            print(f"✅ 已成功导出迭代规划统计到: {self.OUTPUT_FILE}")
            
            # 打印统计结果
            pd.set_option('display.float_format', '{:.2f}'.format)
            print("\n迭代规划统计：")
            print(df.to_string(index=False))
            
        except Exception as e:
            print(f"Error: 保存CSV文件失败: {str(e)}")


def main():
    """主函数"""
    try:
        sprint_planning = SprintPlanning()
        sprint_planning.generate_report()
    except Exception as e:
        print(f"Error: 程序执行出错: {str(e)}")


if __name__ == "__main__":
    main()