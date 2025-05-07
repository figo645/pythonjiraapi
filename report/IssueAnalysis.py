import requests
import urllib.parse
import pandas as pd
import os
import re
import json
from datetime import datetime
import numpy as np
from jiraapi.BaseJira import BaseJira
from jiraapi.config import API_TOKEN, JIRA_EMAIL

class IssueAnalysis(BaseJira):
    def __init__(self):
        super().__init__()
        self.API_TOKEN = API_TOKEN
        self.JIRA_EMAIL = JIRA_EMAIL
        self.JIRA_URL = "https://jira.digitalvolvo.com"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        
        # 根据需求设置的JQL查询
        self.JQL_QUERY = "issuetype in (BA工作任务,任务, 技术需求Enabler, 故事, 测试QA工作任务, 运维任务) AND Sprint in openSprints()"
        
        # 设置基础路径
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.INPUT_FILE = os.path.join(self.BASE_DIR, "data", "issueListReport.csv")
        self.OUTPUT_FILE = os.path.join(self.BASE_DIR, "data", "issue_analysis_report.csv")
        self.DEPARTMENT_OUTPUT_FILE = os.path.join(self.BASE_DIR, "data", "department_workload_report.csv")
        self.CONFIG_FILE = os.path.join(self.BASE_DIR, "jiraapi", "config.json")
        
        # Load configuration
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Validate configuration
            if not isinstance(config.get('sprint_start'), (int, type(None))):
                print("Error: sprint_start must be an integer or null")
                return None
            if not isinstance(config.get('sprint_end'), (int, type(None))):
                print("Error: sprint_end must be an integer or null")
                return None
            if not isinstance(config.get('projects'), dict):
                print("Error: projects must be a dictionary")
                return None
            if not isinstance(config.get('teams'), dict):
                print("Error: teams must be a dictionary")
                return None
            if not isinstance(config.get('team_department_mapping'), dict):
                print("Error: team_department_mapping must be a dictionary")
                return None
            
            return config
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in config.json: {str(e)}")
            return None
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return None

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
            
            # 计算百人天吞吐量
            throughput = (stats["userStoryCount"] / stats["totalUserStoryPoints"] * 100) if stats["totalUserStoryPoints"] > 0 else 0
            
            # 计算CV值（变异系数）
            story_points_list = stats["storyPointsList"]
            cv_value = 0
            if len(story_points_list) > 0:
                mean = np.mean(story_points_list)
                std = np.std(story_points_list)
                cv_value = (std / mean * 100) if mean > 0 else 0
            
            # 计算吞吐量预警
            throughput_warning = "预警" if throughput < 45 else "良好"
            
            # 计算CV值预警
            cv_warning = "良好" if 35 <= cv_value <= 55 else "需改进"
            
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
                "throughput": round(throughput, 2),  # 新增：百人天吞吐量
                "cvValue": round(cv_value, 2),  # 新增：CV值
                "throughputWarning": throughput_warning,  # 新增：吞吐量预警
                "cvWarning": cv_warning  # 新增：CV值预警
            })

        # 创建DataFrame
        df = pd.DataFrame(records)

        # 设置浮点数显示格式
        float_columns = [
            'storypointPlanned', 'storypointCompleted', 'testPoints', 
            'userStoryPoints', 'userStoryRatio', 'enablerPoints', 
            'enablerRatio', 'throughput', 'cvValue'
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

    def load_data(self):
        """Load and preprocess the CSV data"""
        try:
            df = pd.read_csv(self.INPUT_FILE)
            
            # Convert Story Points to numeric
            df['Story Points'] = pd.to_numeric(df['Story Points'], errors='coerce').fillna(0)
            
            # Convert Create Date to datetime
            df['Create Date'] = pd.to_datetime(df['Create Date'])
            
            # Get unique projects and teams
            unique_projects = df['Project'].unique()
            unique_teams = df['Delivery Team'].unique()
            
            # Update configuration with any new projects or teams
            for project in unique_projects:
                if pd.notna(project) and project not in self.config['projects']:
                    self.config['projects'][project] = True
            
            for team in unique_teams:
                if pd.notna(team) and team not in self.config['teams']:
                    self.config['teams'][team] = True
            
            # Save updated configuration
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            print("\nAvailable Projects:")
            for project in sorted(self.config['projects'].keys()):
                print(f"- {project} ({'Included' if self.config['projects'][project] else 'Excluded'})")
            
            print("\nAvailable Teams:")
            for team in sorted(self.config['teams'].keys()):
                print(f"- {team} ({'Included' if self.config['teams'][team] else 'Excluded'})")
            
            return df
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None

    def is_sprint_in_range(self, sprint_name):
        """Check if sprint number is within the specified range"""
        if not isinstance(sprint_name, str):
            return False
            
        # Extract sprint numbers from various formats
        sprint_numbers = re.findall(r'\d+', sprint_name)
        if not sprint_numbers:
            return False
            
        # Get the last number (usually the sprint number)
        sprint_num = int(sprint_numbers[-1])
        
        # Check if sprint range is configured
        if self.config['sprint_start'] is None or self.config['sprint_end'] is None:
            print("Warning: Sprint range not configured in config.json")
            return True  # Return True if no range is specified
        
        return self.config['sprint_start'] <= sprint_num <= self.config['sprint_end']

    def filter_data(self, df):
        """Filter data based on configuration"""
        # Filter by sprint range
        df = df[df['Sprint'].apply(self.is_sprint_in_range)]
        
        # Filter by projects
        if any(self.config['projects'].values()):
            df = df[df['Project'].isin([p for p, include in self.config['projects'].items() if include])]
        
        # Filter by teams
        if any(self.config['teams'].values()):
            df = df[df['Delivery Team'].isin([t for t, include in self.config['teams'].items() if include])]
        
        return df

    def analyze_data(self, df):
        """Analyze the filtered data"""
        results = []
        department_stats = {}
        
        # Group by Project and Delivery Team
        grouped = df.groupby(['Project', 'Delivery Team'])
        
        for (project, team), group in grouped:
            # Calculate total story points
            total_points = group['Story Points'].sum()
            
            # Calculate story points by issue type
            points_by_type = group.groupby('Issue Type')['Story Points'].sum().to_dict()
            
            # Get department from mapping
            department = self.config['team_department_mapping'].get(team, "未分类")
            
            # Calculate user story metrics
            user_stories = group[group['Issue Type'] == '故事']
            user_story_count = len(user_stories)
            user_story_points = user_stories['Story Points'].sum()
            
            # Calculate throughput (百人天吞吐量)
            throughput = (user_story_count / user_story_points * 100) if user_story_points > 0 else 0
            
            # Calculate CV value (变异系数)
            story_points_list = user_stories['Story Points'].tolist()
            cv_value = 0
            if len(story_points_list) > 0:
                mean = np.mean(story_points_list)
                std = np.std(story_points_list)
                cv_value = (std / mean * 100) if mean > 0 else 0
            
            # Calculate warnings
            throughput_warning = "预警" if throughput < 45 else "良好"
            cv_warning = "良好" if 35 <= cv_value <= 55 else "需改进"
            
            # Update department statistics
            if department not in department_stats:
                department_stats[department] = {
                    "total_points": 0,
                    "story_points": 0
                }
            department_stats[department]["total_points"] += total_points
            department_stats[department]["story_points"] += user_story_points
            
            # Create result row
            result = {
                'JIRA项目名': project,
                '交付团队': team,
                '部门': department,
                '总计交付故事点数': total_points,
                '百人天吞吐量': round(throughput, 2),
                'CV值': round(cv_value, 2),
                '吞吐量预警': throughput_warning,
                'CV值预警': cv_warning
            }
            
            # Add points by issue type
            for issue_type, points in points_by_type.items():
                result[f'{issue_type}点数'] = points
            
            results.append(result)
        
        # Generate department workload report
        department_results = []
        for department, stats in department_stats.items():
            total_points = stats["total_points"]
            # Calculate estimated team size: total points / (20 workdays * 3 months)
            estimated_team_size = round(total_points / (20 * 3), 1)
            
            department_results.append({
                "部门": department,
                "投入故事点": total_points,
                "大约团队人数": estimated_team_size
            })
        
        return results, department_results

    def export_results(self, results, department_results):
        """Export analysis results to CSV"""
        try:
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            df_dept = pd.DataFrame(department_results)
            
            # Fill NaN values with 0
            df = df.fillna(0)
            df_dept = df_dept.fillna(0)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.OUTPUT_FILE), exist_ok=True)
            
            # Export to CSV
            df.to_csv(self.OUTPUT_FILE, index=False, encoding='utf-8-sig')
            df_dept.to_csv(self.DEPARTMENT_OUTPUT_FILE, index=False, encoding='utf-8-sig')
            
            print(f"\n✅ Successfully exported analysis results to: {self.OUTPUT_FILE}")
            print(f"✅ Successfully exported department workload to: {self.DEPARTMENT_OUTPUT_FILE}")
            
            # Print summary
            print("\nAnalysis Summary:")
            print(df.to_string(index=False))
            
            print("\nDepartment Workload Summary:")
            print(df_dept.to_string(index=False))
            
        except Exception as e:
            print(f"❌ Error exporting results: {str(e)}")

    def run_analysis(self):
        """Run the complete analysis process"""
        print("Starting issue analysis...")
        
        # Verify configuration
        if self.config is None:
            print("Error: Configuration is invalid")
            return
        
        if self.config['sprint_start'] is None or self.config['sprint_end'] is None:
            print("Warning: Sprint range not configured in config.json")
            print("All sprints will be included in the analysis")
        
        # Load data
        df = self.load_data()
        if df is None:
            return
        
        print(f"Loaded {len(df)} issues")
        
        # Filter data
        filtered_df = self.filter_data(df)
        print(f"Filtered to {len(filtered_df)} issues")
        
        # Analyze data
        results, department_results = self.analyze_data(filtered_df)
        
        # Export results
        self.export_results(results, department_results)

    def update_config_from_report(self):
        """Update config.json based on the analysis report"""
        try:
            # Read the analysis report
            report_file = os.path.join(self.BASE_DIR, "data", "issue_analysis_report.csv")
            if not os.path.exists(report_file):
                print("Analysis report not found. Please run the analysis first.")
                return
            
            df = pd.read_csv(report_file)
            
            # Get unique projects and teams
            unique_projects = df['JIRA项目名'].unique()
            unique_teams = df['交付团队'].unique()
            
            # Update projects in config
            for project in unique_projects:
                if pd.notna(project) and project not in self.config['projects']:
                    self.config['projects'][project] = True
            
            # Update teams in config
            for team in unique_teams:
                if pd.notna(team) and team not in self.config['teams']:
                    self.config['teams'][team] = True
            
            # Save updated configuration
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            print("\nUpdated Projects in config.json:")
            for project in sorted(self.config['projects'].keys()):
                print(f"- {project} ({'Included' if self.config['projects'][project] else 'Excluded'})")
            
            print("\nUpdated Teams in config.json:")
            for team in sorted(self.config['teams'].keys()):
                print(f"- {team} ({'Included' if self.config['teams'][team] else 'Excluded'})")
            
            print(f"\n✅ Successfully updated config.json with {len(unique_projects)} projects and {len(unique_teams)} teams")
            
        except Exception as e:
            print(f"Error updating config from report: {str(e)}")

def main():
    """Main function"""
    try:
        # Create analyzer instance
        analyzer = IssueAnalysis()
        
        # Update configuration from report
        analyzer.update_config_from_report()
        
        # Verify configuration
        if analyzer.config['sprint_start'] is None or analyzer.config['sprint_end'] is None:
            print("Error: Please configure sprint_start and sprint_end in config.json")
            return
            
        # Run analysis
        analyzer.run_analysis()
        
    except Exception as e:
        print(f"Error: Program execution failed: {str(e)}")

if __name__ == "__main__":
    main() 