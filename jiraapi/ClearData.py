import os
import psycopg2
from datetime import datetime

class ClearData:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.BASE_DIR, "data")
        self.conn = psycopg2.connect(
            dbname="jira_metrics",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432"
        )
        self.cursor = self.conn.cursor()
        self.tables = [
            "bug_progress",
            "change_tracking",
            "iteration_completion",
            "sprint_planning",
            "testing_progress"
        ]

    def clear_all_data(self):
        """删除所有记录"""
        try:
            for table_name in self.tables:
                self.cursor.execute(f"DELETE FROM {table_name}")
                self.conn.commit()
                print(f"✅ Successfully cleared all data from table {table_name}")
        except Exception as e:
            print(f"Error clearing data: {e}")
            self.conn.rollback()
        finally:
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    clear_data = ClearData()
    clear_data.clear_all_data() 