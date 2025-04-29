import requests
import pandas as pd
import os
from datetime import datetime
import urllib.parse

class TestCasesAnalyzer:
    def __init__(self):
        # Jira API configuration
        self.JIRA_URL = "https://jira.digitalvolvo.com"
        self.API_TOKEN = "MDQ3NDAxMzQ2ODY0OiksiKm1bWeZ1sAfWgqRfQ2WrgPV"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        
        # Set output directory
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.OUTPUT_DIR = os.path.join(self.BASE_DIR, "data")
        
        # JQL query for test plans
        self.JQL_QUERY = 'issuetype = "测试计划" AND Sprint in openSprints()'

    def get_test_plans(self):
        """Get all test plans based on JQL query"""
        try:
            jql_encoded = urllib.parse.quote(self.JQL_QUERY)
            url = f"{self.JIRA_URL}/rest/api/2/search?jql={jql_encoded}&maxResults=1000"
            print(f"\nGetting test plans with JQL: {self.JQL_QUERY}")
            
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to get test plans, status code: {response.status_code}")
                return []
            
            data = response.json()
            return data.get('issues', [])
        except Exception as e:
            print(f"Error getting test plans: {str(e)}")
            return []

    def get_test_cases_for_plan(self, test_plan_key):
        """Get all test cases for a specific test plan"""
        try:
            url = f"{self.JIRA_URL}/rest/synapse/latest/public/testPlan/{test_plan_key}/members"
            print(f"\nGetting test cases for test plan: {test_plan_key}")
            
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to get test cases for plan {test_plan_key}, status code: {response.status_code}")
                return []
            
            test_cases = response.json()
            print(f"Found {len(test_cases)} test cases for plan {test_plan_key}")
            return test_cases
        except Exception as e:
            print(f"Error getting test cases for plan {test_plan_key}: {str(e)}")
            return []

    def analyze_test_cases(self):
        """Analyze test case status for all test plans"""
        try:
            # Get all test plans
            test_plans = self.get_test_plans()
            if not test_plans:
                print("No test plans found")
                return None

            print(f"\nFound {len(test_plans)} test plans")
            
            # Initialize team statistics
            team_stats = {}

            # Analyze each test plan
            for plan in test_plans:
                try:
                    plan_key = plan['key']
                    fields = plan['fields']
                    
                    # Get delivery team information
                    team_field = fields.get('customfield_11101', {})
                    team_name = team_field.get('child', {}).get('value', 'Unassigned Team')
                    
                    print(f"\nProcessing test plan {plan_key} for team {team_name}")
                    
                    # Initialize team statistics if not exists
                    if team_name not in team_stats:
                        team_stats[team_name] = {
                            'total_test_cases': 0,
                            'completed_test_cases': 0,
                            'failed_test_cases': 0,
                            'blocked_test_cases': 0
                        }

                    # Get test cases for this plan
                    test_cases = self.get_test_cases_for_plan(plan_key)
                    
                    # Update test case statistics
                    team_stats[team_name]['total_test_cases'] += len(test_cases)
                    
                    for test_case in test_cases:
                        # Safely get status with default value
                        status = test_case.get('status', 'Not Run')
                        
                        if status in ['通过', 'Approved']:
                            team_stats[team_name]['completed_test_cases'] += 1
                        elif status in ['失败', 'Failed']:
                            team_stats[team_name]['failed_test_cases'] += 1
                        elif status in ['阻塞', 'Blocked']:
                            team_stats[team_name]['blocked_test_cases'] += 1

                    print(f"Updated statistics for team {team_name}:")
                    print(f"  Total test cases: {team_stats[team_name]['total_test_cases']}")
                    print(f"  Completed: {team_stats[team_name]['completed_test_cases']}")
                    print(f"  Failed: {team_stats[team_name]['failed_test_cases']}")
                    print(f"  Blocked: {team_stats[team_name]['blocked_test_cases']}")
                
                except Exception as e:
                    print(f"Error processing test plan {plan.get('key', 'Unknown')}: {str(e)}")
                    continue

            return team_stats
        except Exception as e:
            print(f"Error analyzing test cases: {str(e)}")
            return None

    def export_to_csv(self, team_stats):
        """Export analysis results to CSV file"""
        try:
            # Ensure output directory exists
            os.makedirs(self.OUTPUT_DIR, exist_ok=True)

            # Create DataFrame from team statistics
            data = []
            for team_name, stats in team_stats.items():
                data.append({
                    'teamName': team_name,
                    'totalTestCases': stats['total_test_cases'],
                    'completedTestCases': stats['completed_test_cases'],
                    'failedTestCases': stats['failed_test_cases'],
                    'blockedTestCases': stats['blocked_test_cases']
                })

            df = pd.DataFrame(data)

            # Export to CSV
            output_file = os.path.join(self.OUTPUT_DIR, 'testing_progress.csv')
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ Successfully exported analysis results to: {output_file}")

            # Print statistics in the requested format
            print("\nTest Case Analysis Statistics:")
            print("teamName,totalTestCases,completedTestCases,failedTestCases,blockedTestCases")
            for _, row in df.iterrows():
                print(f"{row['teamName']},{row['totalTestCases']},{row['completedTestCases']},"
                      f"{row['failedTestCases']},{row['blockedTestCases']}")

        except Exception as e:
            print(f"❌ Error exporting analysis results: {str(e)}")

    def run_analysis(self):
        """Run the analysis process"""
        print(f"\nStarting analysis for test plans in open sprints...")
        
        # Analyze test cases
        team_stats = self.analyze_test_cases()
        if team_stats:
            # Export results
            self.export_to_csv(team_stats)
        else:
            print("❌ Analysis failed, please check logs")

if __name__ == "__main__":
    # Run analysis
    analyzer = TestCasesAnalyzer()
    analyzer.run_analysis()
