import psycopg2
import pandas as pd
from datetime import datetime
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 数据库连接配置
DB_CONFIG = {
    'dbname': 'sprint_dashboard',
    'user': 'postgres',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}


def import_csv_to_postgres(csv_file, table_name, data_date):
    try:
        # 读取CSV文件
        logger.info(f"Reading CSV file: {csv_file}")
        df = pd.read_csv(csv_file)

        # 添加数据日期列
        df['data_date'] = data_date

        # 连接数据库
        logger.info("Connecting to database")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 准备插入语句
        columns = ', '.join(df.columns)
        values = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"

        # 执行批量插入
        logger.info(f"Importing data into {table_name}")
        cursor.executemany(insert_query, df.values.tolist())

        # 提交事务
        conn.commit()
        logger.info(f"Successfully imported {len(df)} rows into {table_name}")

    except Exception as e:
        logger.error(f"Error importing {csv_file}: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()


def main():
    # 设置数据日期（可以根据需要修改）
    data_date = datetime.now().date()

    # CSV文件路径
    csv_files = {
        'sprint_planning': 'path/to/sprint_planning.csv',
        'iteration_completion': 'path/to/iteration_completion.csv',
        'bug': 'path/to/bug.csv',
        'change': 'path/to/change.csv',
        'testing': 'path/to/testing.csv'
    }

    # 导入每个CSV文件
    for table_name, csv_file in csv_files.items():
        if os.path.exists(csv_file):
            import_csv_to_postgres(csv_file, table_name, data_date)
        else:
            logger.warning(f"CSV file not found: {csv_file}")


if __name__ == "__main__":
    main()