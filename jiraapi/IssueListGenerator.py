import requests
import urllib.parse
import pandas as pd
import os
from datetime import datetime
from jiraapi.BaseJira import BaseJira
from jiraapi.config import API_TOKEN, JIRA_EMAIL

class IssueListGenerator(BaseJira):
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
        
        # JQL query
        self.JQL_QUERY = 'issuetype in (BA工作任务, 任务, 技术需求Enabler, 故事, 测试QA工作任务, 运维任务) AND created >= 2024-12-01 AND created <= 2025-04-01'

    def get_issues(self):
        """Get all issues based on JQL query"""
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
                print(f"Error: Failed to get JIRA data: {str(e)}")
                break

        return all_issues

    def process_issues(self, issues):
        """Process issues and extract required fields"""
        processed_issues = []
        
        for issue in issues:
            fields = issue['fields']
            
            # Extract required fields
            issue_data = {
                'Issue Key': issue['key'],
                'Project': fields.get('project', {}).get('name', ''),
                'Summary': fields.get('summary', ''),
                'Issue Type': fields.get('issuetype', {}).get('name', ''),
                'Epic Link': fields.get('customfield_10014', ''),
                'Create Date': fields.get('created', ''),
                'Story Points': fields.get('customfield_10106', 0),
                'Sprint': self._get_sprint_name(fields.get('customfield_10104', [])),
                'Delivery Team': self._get_delivery_team(fields.get('customfield_11101', {})),
                'Status': fields.get('status', {}).get('name', '')
            }
            
            processed_issues.append(issue_data)
        
        return processed_issues

    def _get_sprint_name(self, sprint_field):
        """Extract sprint name from sprint field"""
        if not sprint_field:
            return ''
        
        # Get the most recent sprint
        sprint = sprint_field[-1] if isinstance(sprint_field, list) else sprint_field
        if isinstance(sprint, str):
            # Extract sprint name from sprint string
            # Format is like: "com.atlassian.greenhopper.service.sprint.Sprint@20be031a[id=1102,rapidViewId=480,state=FUTURE,name=25年-自营项目【5月】Sprint77-78,startDate=<null>,endDate=<null>,completeDate=<null>,activatedDate=<null>,sequence=1102,goal=<null>,synced=false,autoStartStop=false,incompleteIssuesDestinationId=<null>]"
            import re
            match = re.search(r'name=([^,]+)', sprint)
            if match:
                return match.group(1)
            else:
                print(f"Warning: Could not extract sprint name from: {sprint}")
        return ''

    def _get_delivery_team(self, team_field):
        """Extract delivery team name from team field"""
        if not team_field:
            return 'Unassigned Team'
        
        return team_field.get('child', {}).get('value', 'Unassigned Team')

    def export_to_csv(self, issues):
        """Export issues to CSV file"""
        try:
            # Ensure output directory exists
            os.makedirs(self.OUTPUT_DIR, exist_ok=True)
            
            # Create DataFrame
            df = pd.DataFrame(issues)
            
            # Format dates
            df['Create Date'] = pd.to_datetime(df['Create Date']).dt.strftime('%Y-%m-%d')
            
            # Export to CSV
            output_file = os.path.join(self.OUTPUT_DIR, 'issueListReport.csv')
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ Successfully exported issue list to: {output_file}")
            
            # Print summary
            print("\nIssue List Summary:")
            print(f"Total issues: {len(issues)}")
            print("\nIssues by type:")
            print(df['Issue Type'].value_counts())
            
        except Exception as e:
            print(f"❌ Error exporting issue list: {str(e)}")

    def run(self):
        """Run the issue list generation process"""
        print("Starting issue list generation...")
        print(f"JQL Query: {self.JQL_QUERY}")
        
        # Get issues
        issues = self.get_issues()
        if not issues:
            print("No issues found")
            return
        
        print(f"Found {len(issues)} issues")
        
        # Process issues
        processed_issues = self.process_issues(issues)
        
        # Export to CSV
        self.export_to_csv(processed_issues)

def main():
    """Main function"""
    try:
        generator = IssueListGenerator()
        generator.run()
    except Exception as e:
        print(f"Error: Program execution failed: {str(e)}")

if __name__ == "__main__":
    main() 