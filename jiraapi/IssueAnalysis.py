import pandas as pd
import os
import re
import json
from datetime import datetime

class IssueAnalysis:
    def __init__(self):
        # Set input and output directories
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.INPUT_FILE = os.path.join(self.BASE_DIR, "data", "issueListReport.csv")
        self.OUTPUT_FILE = os.path.join(self.BASE_DIR, "data", "issue_analysis_report.csv")
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
            
            return config
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in config.json: {str(e)}")
            return None
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return None

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
        
        # Group by Project and Delivery Team
        grouped = df.groupby(['Project', 'Delivery Team'])
        
        for (project, team), group in grouped:
            # Calculate total story points
            total_points = group['Story Points'].sum()
            
            # Calculate story points by issue type
            points_by_type = group.groupby('Issue Type')['Story Points'].sum().to_dict()
            
            # Create result row
            result = {
                'JIRA项目名': project,
                '交付团队': team,
                '总计交付故事点数': total_points
            }
            
            # Add points by issue type
            for issue_type, points in points_by_type.items():
                result[f'{issue_type}点数'] = points
            
            results.append(result)
        
        return results

    def export_results(self, results):
        """Export analysis results to CSV"""
        try:
            # Convert results to DataFrame
            df = pd.DataFrame(results)
            
            # Fill NaN values with 0
            df = df.fillna(0)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(self.OUTPUT_FILE), exist_ok=True)
            
            # Export to CSV
            df.to_csv(self.OUTPUT_FILE, index=False, encoding='utf-8-sig')
            print(f"\n✅ Successfully exported analysis results to: {self.OUTPUT_FILE}")
            
            # Print summary
            print("\nAnalysis Summary:")
            print(df.to_string(index=False))
            
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
        results = self.analyze_data(filtered_df)
        
        # Export results
        self.export_results(results)

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