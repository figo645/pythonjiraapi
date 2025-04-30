import requests
import urllib.parse
import pandas as pd
import os
from datetime import datetime
from .BaseJira import BaseJira

class ChangeTracking(BaseJira):
    def __init__(self):
        super().__init__()
        # Jira API 相关信息
        self.JIRA_URL = "https://jira.digitalvolvo.com"
        
        # 根据需求设置的JQL查询 - 查询带有"变更"标签的问题
        self.JQL_QUERY = "labels in (变更) AND Sprint in openSprints()"
        
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        # 设置基础路径
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 输出文件路径
        self.OUTPUT_FILE = os.path.join(self.BASE_DIR, "data", "change_tracking.csv")

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
            team_name = team_field.get('child', {}).get('value') if team_field and 'child' in team_field else "Unassigned Team"
            
            # 获取故事点
            story_points = fields.get('customfield_10106', 0) or 0
            
            # 检查标签中是否包含"变更"
            labels = fields.get('labels', [])
            has_change_label = any("变更" in label for label in labels)
            
            if has_change_label:
                # 初始化团队数据
                if team_name not in team_stats:
                    team_stats[team_name] = {
                        "changeTasks": 0,
                        "changePoints": 0
                    }
                
                # 更新变更任务数和点数
                team_stats[team_name]["changeTasks"] += 1
                team_stats[team_name]["changePoints"] += story_points

        return team_stats

    def generate_report(self):
        """生成变更跟踪报告"""
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
                "teamName": team,
                "changeTasks": stats["changeTasks"],
                "changePoints": round(stats["changePoints"], 2)  # 保留2位小数
            })

        # 创建DataFrame
        df = pd.DataFrame(records)

        # 设置浮点数显示格式
        float_columns = ['changePoints']
        for col in float_columns:
            df[col] = df[col].round(2)

        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(self.OUTPUT_FILE), exist_ok=True)
            
            # 保存到CSV文件，设置浮点数格式
            df.to_csv(self.OUTPUT_FILE, index=False, encoding='utf-8-sig', float_format='%.2f')
            print(f"✅ 已成功导出变更跟踪统计到: {self.OUTPUT_FILE}")
            
            # 打印统计结果
            pd.set_option('display.float_format', '{:.2f}'.format)
            print("\n变更跟踪统计：")
            print(df.to_string(index=False))
            
        except Exception as e:
            print(f"Error: 保存CSV文件失败: {str(e)}")

    def export_to_csv(self, results):
        """Export analysis results to CSV file"""
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.OUTPUT_FILE), exist_ok=True)

            # Create DataFrame and export to CSV
            df = pd.DataFrame(results)
            output_file = self.OUTPUT_FILE
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ Successfully exported analysis results to: {output_file}")

            # Print statistics in the requested format
            print("\nChange Tracking Statistics:")
            print("teamName,totalStories,completedStories,storyPoints,completedStoryPoints")
            for result in results:
                print(f"{result['teamName']},{result['totalStories']},{result['completedStories']},"
                      f"{result['storyPoints']},{result['completedStoryPoints']}")

        except Exception as e:
            print(f"❌ Error exporting analysis results: {str(e)}")

    def analyze_changes(self):
        """Analyze changes across all teams"""
        try:
            # Get all issues
            issues = self.get_jira_issues()
            if not issues:
                print("No issues found")
                return []
            
            # Initialize team statistics
            team_stats = {}
            
            for issue in issues:
                try:
                    # Get delivery team name from custom field
                    team_field = issue['fields'].get('customfield_11101', {})
                    team_name = team_field.get('child', {}).get('value', 'Unassigned Team')
                    
                    # Initialize team statistics if not exists
                    if team_name not in team_stats:
                        team_stats[team_name] = {
                            'total_stories': 0,
                            'completed_stories': 0,
                            'story_points': 0,
                            'completed_story_points': 0
                        }
                    
                    # Update statistics
                    team_stats[team_name]['total_stories'] += 1
                    
                    # Get story points
                    story_points = issue['fields'].get('customfield_10106', 0)
                    team_stats[team_name]['story_points'] += story_points
                    
                    # Check if story is completed
                    status = issue['fields']['status']['name']
                    if status in ['Done', '完成']:
                        team_stats[team_name]['completed_stories'] += 1
                        team_stats[team_name]['completed_story_points'] += story_points
                        
                except Exception as e:
                    print(f"Error processing issue {issue.get('key', 'Unknown')}: {str(e)}")
                    continue
            
            # Convert team statistics to the required format
            results = []
            for team_name, stats in team_stats.items():
                results.append({
                    'teamName': team_name,
                    'totalStories': stats['total_stories'],
                    'completedStories': stats['completed_stories'],
                    'storyPoints': stats['story_points'],
                    'completedStoryPoints': stats['completed_story_points']
                })
            
            return results
        except Exception as e:
            print(f"Error analyzing changes: {str(e)}")
            return []

def main():
    """主函数"""
    try:
        change_tracking = ChangeTracking()
        change_tracking.generate_report()
    except Exception as e:
        print(f"Error: 程序执行出错: {str(e)}")

if __name__ == "__main__":
    main()