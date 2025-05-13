import os
import pandas as pd
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
import csv

class DatabaseManager:
    def __init__(self):
        # Database connection parameters
        self.db_params = {
            'dbname': 'sprint_dashboard',
            'user': 'postgres',
            'password': 'your_password',
            'host': '129.211.65.53',
            'port': '5432'
        }
        
        # Base directory for CSV files
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data")
        
        # Current date information
        self.current_date = datetime.now()
        self.date_date = self.current_date.strftime('%Y-%m-%d')
        self.date_month = self.current_date.strftime('%Y-%m')
        self.date_quarter = f"{self.current_date.year}-Q{(self.current_date.month-1)//3 + 1}"

        # Column mapping for each table
        self.column_mapping = {
            'sprint_planning': {
                'programName': 'program_name',
                'teamName': 'team_name',
                'plannedProgress': 'planned_count',
                'actualProgress': 'completed_count',
                'storypointPlanned': 'storypoint_planned',
                'storypointCompleted': 'storypoint_completed',
                'testPoints': 'test_points',
                'userStoryPoints': 'user_story_points',
                'userStoryRatio': 'user_story_ratio',
                'enablerPoints': 'enabler_points',
                'enablerRatio': 'enabler_ratio',
                'storyThroughput': 'story_throughput',
                'cvValue': 'cv_value',
                'storyGranularity': 'story_granularity'
            },
            'iteration_completion': {
                'programName': 'program_name',
                'teamName': 'team_name',
                'plannedProgress': 'planned_progress',
                'actualProgress': 'actual_progress',
                'storypointPlanned': 'storypoint_planned',
                'storypointCompleted': 'storypoint_completed'
            },
            'bug_progress': {
                'programName': 'program_name',
                'teamName': 'team_name',
                'totalBugs': 'total_bugs',
                'preFixed': 'pre_fixed',
                'uatFixed': 'uat_fixed',
                'prePending': 'pre_pending',
                'uatPending': 'uat_pending',
                'preFixedRatio': 'pre_fixed_ratio',
                'uatFixedRatio': 'uat_fixed_ratio'
            },
            'change_tracking': {
                'teamName': 'team_name',
                'changeTasks': 'change_tasks',
                'changePoints': 'change_points'
            },
            'testing_progress': {
                'teamName': 'team_name',
                'totalTestCases': 'total_test_cases',
                'completedTestCases': 'completed_test_cases',
                'failedTestCases': 'failed_test_cases',
                'blockedTestCases': 'blocked_test_cases'
            }
        }

    def get_connection(self):
        """Establish database connection"""
        try:
            conn = psycopg2.connect(**self.db_params)
            return conn
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            return None

    def map_columns(self, df, table_name):
        """Map CSV column names to database column names"""
        if table_name in self.column_mapping:
            mapping = self.column_mapping[table_name]
            df = df.rename(columns=mapping)
        return df

    def clear_table(self, table_name):
        """Clear all contents from specified table"""
        conn = self.get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                # Create SQL query to delete all rows
                query = sql.SQL("DELETE FROM {}").format(
                    sql.Identifier(table_name)
                )
                cur.execute(query)
                conn.commit()
                print(f"✅ Successfully cleared table {table_name}")
                return True

        except Exception as e:
            print(f"Error clearing table {table_name}: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def insert_data(self, table_name, df):
        """Insert data into specified table"""
        conn = self.get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                # Clear existing data first
                self.clear_table(table_name)
                
                # Map column names
                df = self.map_columns(df, table_name)
                
                # Add date columns to DataFrame
                df['data_date'] = self.date_date
                df['data_month'] = self.date_month
                df['data_quarter'] = self.date_quarter

                # For testing_progress table, remove total_testplan if it exists
                if table_name == 'testing_progress' and 'total_testplan' in df.columns:
                    df = df.drop(columns=['total_testplan'])

                # Prepare columns and values for insertion
                columns = df.columns.tolist()
                values = [tuple(x) for x in df.values]

                # Create SQL query
                query = sql.SQL("INSERT INTO {} ({}) VALUES %s").format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, columns))
                )

                # Execute the query
                execute_values(cur, query, values)
                conn.commit()
                print(f"✅ Successfully inserted data into {table_name}")
                return True

        except Exception as e:
            print(f"Error inserting data into {table_name}: {str(e)}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def process_all_csv_files(self):
        """Process all CSV files in the data directory"""
        csv_files = {
            'bug_progress': 'bug_progress.csv',
            'change_tracking': 'change_tracking.csv',
            'iteration_completion': 'iteration_completion.csv',
            'sprint_planning': 'sprint_planning.csv',
            'testing_progress': 'testing_progress.csv'
        }

        for table_name, csv_file in csv_files.items():
            file_path = os.path.join(self.DATA_DIR, csv_file)
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    self.insert_data(table_name, df)
                except Exception as e:
                    print(f"Error processing {csv_file}: {str(e)}")
            else:
                print(f"Warning: {csv_file} not found in data directory")

    def import_data_from_csv(self):
        """从CSV文件导入数据到数据库"""
        try:
            # 获取当前日期
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # 删除当天的所有表数据
            for table_name in self.tables:
                self.cursor.execute(f"DELETE FROM {table_name} WHERE data_date = %s", (current_date,))
                self.conn.commit()
                print(f"✅ Successfully cleared table {table_name} for date {current_date}")
            
            # 导入数据
            for table_name, csv_file in self.csv_files.items():
                if os.path.exists(csv_file):
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            # 确保data_date字段存在
                            if 'data_date' not in row:
                                row['data_date'] = current_date
                            
                            # 构建INSERT语句
                            columns = ', '.join([f'"{k}"' for k in row.keys()])
                            values = ', '.join(['%s'] * len(row))
                            query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({values})'
                            
                            try:
                                self.cursor.execute(query, list(row.values()))
                                self.conn.commit()
                            except Exception as e:
                                print(f"Error inserting data into {table_name}: {e}")
                                self.conn.rollback()
                    print(f"✅ Successfully inserted data into {table_name}")
                else:
                    print(f"⚠️ CSV file not found: {csv_file}")
        except Exception as e:
            print(f"Error importing data: {e}")
            self.conn.rollback()

def main():
    """Main function to run the database operations"""
    try:
        db_manager = DatabaseManager()
        db_manager.process_all_csv_files()
    except Exception as e:
        print(f"Error in main execution: {str(e)}")

if __name__ == "__main__":
    main() 