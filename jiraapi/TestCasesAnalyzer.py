import requests
import pandas as pd
import os
from datetime import datetime
import urllib.parse
from jiraapi.BaseJira import BaseJira
from jiraapi.config import API_TOKEN, JIRA_EMAIL

class TestCasesAnalyzer(BaseJira):
    def __init__(self):
        super().__init__()
        self.API_TOKEN = API_TOKEN
        self.JIRA_EMAIL = JIRA_EMAIL
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
            # First try the Synapse API endpoint
            url = f"{self.JIRA_URL}/rest/synapse/latest/public/testPlan/{test_plan_key}/testCases"
            print(f"\nGetting test cases for test plan: {test_plan_key}")
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 404:
                print(f"Test plan {test_plan_key} not found in Synapse. Trying alternative endpoint...")
                
                # First get test plan details to inspect its fields
                url = f"{self.JIRA_URL}/rest/api/2/issue/{test_plan_key}"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code != 200:
                    print(f"Failed to get test plan details for {test_plan_key}, status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    return []
                
                issue_data = response.json()
                fields = issue_data.get('fields', {})
                
                # Print available fields for debugging
                print(f"Available fields for test plan {test_plan_key}:")
                for field_name, field_value in fields.items():
                    if field_value:  # Only print non-empty fields
                        print(f"  {field_name}: {field_value}")
                
                # Try different search approaches
                test_cases = []
                
                # Approach 1: Search by test plan key in description or summary
                search_url = f"{self.JIRA_URL}/rest/api/2/search"
                search_query = f'project = {test_plan_key.split("-")[0]} AND issuetype = "测试用例" AND (description ~ "{test_plan_key}" OR summary ~ "{test_plan_key}")'
                search_params = {
                    'jql': search_query,
                    'maxResults': 1000
                }
                
                response = requests.get(search_url, headers=self.headers, params=search_params)
                if response.status_code == 200:
                    search_results = response.json()
                    test_cases.extend(search_results.get('issues', []))
                
                # Approach 2: Search by custom field if we find one
                for field_name, field_value in fields.items():
                    if isinstance(field_value, dict) and 'value' in field_value:
                        custom_field_value = field_value['value']
                        search_query = f'project = {test_plan_key.split("-")[0]} AND issuetype = "测试用例" AND {field_name} = "{custom_field_value}"'
                        search_params = {
                            'jql': search_query,
                            'maxResults': 1000
                        }
                        
                        response = requests.get(search_url, headers=self.headers, params=search_params)
                        if response.status_code == 200:
                            search_results = response.json()
                            test_cases.extend(search_results.get('issues', []))
                
                if not test_cases:
                    print(f"No test cases found for test plan {test_plan_key}")
                    return []
                
                # Remove duplicates
                unique_test_cases = []
                seen_keys = set()
                for case in test_cases:
                    if case['key'] not in seen_keys:
                        seen_keys.add(case['key'])
                        unique_test_cases.append(case)
                
                print(f"Found {len(unique_test_cases)} test cases for plan {test_plan_key}")
                return unique_test_cases
            else:
                if response.status_code != 200:
                    print(f"Failed to get test cases for plan {test_plan_key}, status code: {response.status_code}")
                    print(f"Response: {response.text}")
                    return []
                
                test_cases = response.json()
                print(f"Found {len(test_cases)} test cases for plan {test_plan_key}")
                return test_cases
        except Exception as e:
            print(f"Error getting test cases for plan {test_plan_key}: {str(e)}")
            return []

    def get_test_case_execution_status(self, test_case_key):
        """Get execution status for a specific test case"""
        try:
            url = f"{self.JIRA_URL}/rest/synapse/latest/public/testRun/{test_case_key}/testRuns"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                print(f"Failed to get execution status for test case {test_case_key}, status code: {response.status_code}")
                return None
            
            test_runs = response.json()
            if not test_runs:
                return None
            
            # Get the most recent test run
            latest_run = test_runs[0]
            return {
                'status': latest_run.get('status'),
                'execution_date': latest_run.get('executionOn'),
                'tester': latest_run.get('testerName'),
                'test_plan': latest_run.get('testPlanKey'),
                'test_cycle': latest_run.get('testCycleSummary'),
                'steps': [{
                    'step': step.get('step'),
                    'status': step.get('status'),
                    'expected_result': step.get('expectedResult')
                } for step in latest_run.get('testRunDetails', {}).get('testRunSteps', [])]
            }
        except Exception as e:
            print(f"Error getting execution status for test case {test_case_key}: {str(e)}")
            return None

    def get_test_plan_information(self, test_plan_key):
        """Get detailed information about a test plan including test cycles and execution status"""
        try:
            url = f"{self.JIRA_URL}/rest/synapse/latest/public/testPlan/{test_plan_key}/testPlanInformation"
            print(f"\nGetting test plan information for: {test_plan_key}")
            
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to get test plan information for {test_plan_key}, status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
            
            data = response.json()
            if not data:
                print(f"No data returned for test plan {test_plan_key}")
                return None
                
            # Check if we have the expected data structure
            if 'testCycles' not in data or 'cycleWithRuns' not in data:
                print(f"Unexpected data structure for test plan {test_plan_key}")
                print(f"Data: {data}")
                return None
                
            return data
        except Exception as e:
            print(f"Error getting test plan information for {test_plan_key}: {str(e)}")
            return None

    def analyze_test_cases(self):
        """Analyze test case statuses across all test plans"""
        try:
            test_plans = self.get_test_plans()
            if not test_plans:
                print("No test plans found")
                return []
            
            # Initialize team statistics
            team_stats = {}
            
            for plan in test_plans:
                try:
                    plan_key = plan['key']
                    plan_name = plan['fields']['summary']
                    
                    # Get delivery team name from custom field
                    team_field = plan['fields'].get('customfield_11101', {})
                    team_name = team_field.get('child', {}).get('value', 'Unassigned Team')
                    
                    print(f"\nProcessing test plan: {plan_key} ({plan_name}) for team: {team_name}")
                    
                    # Initialize team statistics if not exists
                    if team_name not in team_stats:
                        team_stats[team_name] = {
                            'total_test_cases': 0,
                            'completed_test_cases': 0,
                            'failed_test_cases': 0,
                            'blocked_test_cases': 0,
                            'seen_test_cases': set()  # To track unique test cases across plans
                        }
                    
                    # Get test plan information
                    plan_info = self.get_test_plan_information(plan_key)
                    if not plan_info:
                        print(f"Skipping test plan {plan_key} due to missing information")
                        continue
                    
                    # Process each test cycle
                    cycle_with_runs = plan_info.get('cycleWithRuns', {})
                    if not cycle_with_runs:
                        print(f"No test cycles found for test plan {plan_key}")
                        continue
                    
                    for cycle_name, test_runs in cycle_with_runs.items():
                        if not test_runs:
                            print(f"No test runs found in cycle {cycle_name} for test plan {plan_key}")
                            continue
                            
                        for test_run in test_runs:
                            test_case_key = test_run.get('testCaseKey')
                            if not test_case_key or test_case_key in team_stats[team_name]['seen_test_cases']:
                                continue
                                
                            team_stats[team_name]['seen_test_cases'].add(test_case_key)
                            team_stats[team_name]['total_test_cases'] += 1
                            
                            status = test_run.get('status', '')
                            if status == '通过':
                                team_stats[team_name]['completed_test_cases'] += 1
                            elif status == '失败':
                                team_stats[team_name]['failed_test_cases'] += 1
                            elif status == '锁定':
                                team_stats[team_name]['blocked_test_cases'] += 1
                except Exception as e:
                    print(f"Error processing test plan {plan.get('key', 'Unknown')}: {str(e)}")
                    continue
            
            # Convert team statistics to the required format
            results = []
            for team_name, stats in team_stats.items():
                results.append({
                    'teamName': team_name,
                    'totalTestCases': stats['total_test_cases'],
                    'completedTestCases': stats['completed_test_cases'],
                    'failedTestCases': stats['failed_test_cases'],
                    'blockedTestCases': stats['blocked_test_cases']
                })
            
            return results
        except Exception as e:
            print(f"Error analyzing test cases: {str(e)}")
            return []

    def export_to_csv(self, results):
        """Export analysis results to CSV file"""
        try:
            # Ensure output directory exists
            os.makedirs(self.OUTPUT_DIR, exist_ok=True)

            # Create DataFrame and export to CSV
            df = pd.DataFrame(results)
            output_file = os.path.join(self.OUTPUT_DIR, 'testing_progress.csv')
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ Successfully exported analysis results to: {output_file}")

            # Print statistics in the requested format
            print("\nTest Case Analysis Statistics:")
            print("teamName,totalTestCases,completedTestCases,failedTestCases,blockedTestCases")
            for result in results:
                print(f"{result['teamName']},{result['totalTestCases']},{result['completedTestCases']},"
                      f"{result['failedTestCases']},{result['blockedTestCases']}")

        except Exception as e:
            print(f"❌ Error exporting analysis results: {str(e)}")

    def run_analysis(self):
        """Run the analysis process"""
        print(f"\nStarting analysis for test plans in open sprints...")
        
        # Analyze test cases
        results = self.analyze_test_cases()
        if results:
            # Export results
            self.export_to_csv(results)
        else:
            print("❌ Analysis failed, please check logs")

if __name__ == "__main__":
    # Run analysis
    analyzer = TestCasesAnalyzer()
    analyzer.run_analysis()
