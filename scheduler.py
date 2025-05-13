import schedule
import time
import logging
import os
import argparse
from datetime import datetime
from jiraapi.BugProgress import BugProgress
from jiraapi.ChangeTracking import ChangeTracking
from jiraapi.IterationCompletion import IterationCompletion
from jiraapi.SprintPlanning import SprintPlanning
from jiraapi.TestCasesAnalyzer import TestCasesAnalyzer
from jiraapi.ClearData import ClearData
from jiraapi.DatabaseManager import DatabaseManager
from jiraapi.config import SCHEDULER_CONFIG

# 配置日志
logging.basicConfig(
    level=getattr(logging, SCHEDULER_CONFIG['LOG_LEVEL']),
    format=SCHEDULER_CONFIG['LOG_FORMAT'],
    handlers=[
        logging.FileHandler(SCHEDULER_CONFIG['LOG_FILE']),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_data_extraction():
    """执行数据抽取任务"""
    try:
        logger.info("开始执行数据抽取任务")
        
        # 执行各个数据抽取任务
        tasks = [
            ("BugProgress", BugProgress()),
            ("ChangeTracking", ChangeTracking()),
            ("IterationCompletion", IterationCompletion()),
            ("SprintPlanning", SprintPlanning()),
            ("TestCasesAnalyzer", TestCasesAnalyzer())
        ]
        
        for task_name, task in tasks:
            # 检查任务是否启用
            if not SCHEDULER_CONFIG['TASKS']['DATA_EXTRACTION'].get(task_name, True):
                logger.info(f"跳过 {task_name} 任务（已禁用）")
                continue
                
            try:
                logger.info(f"开始执行 {task_name}")
                task.run()
                logger.info(f"{task_name} 执行完成")
            except Exception as e:
                logger.error(f"{task_name} 执行失败: {str(e)}")
                return False
                
        logger.info("所有数据抽取任务执行完成")
        return True
                
    except Exception as e:
        logger.error(f"数据抽取任务执行失败: {str(e)}")
        return False

def run_data_import():
    """执行数据导入任务"""
    try:
        logger.info("开始执行数据导入任务")
        
        # 清除数据
        if SCHEDULER_CONFIG['TASKS']['DATA_IMPORT'].get('ClearData', True):
            try:
                logger.info("开始清除数据")
                clear_data = ClearData()
                clear_data.clear_all_data()
                logger.info("数据清除完成")
            except Exception as e:
                logger.error(f"数据清除失败: {str(e)}")
                return False
        else:
            logger.info("跳过数据清除任务（已禁用）")
        
        # 导入数据
        if SCHEDULER_CONFIG['TASKS']['DATA_IMPORT'].get('DatabaseManager', True):
            try:
                logger.info("开始导入数据")
                db_manager = DatabaseManager()
                db_manager.process_all_csv_files()
                logger.info("数据导入完成")
                return True
            except Exception as e:
                logger.error(f"数据导入失败: {str(e)}")
                return False
        else:
            logger.info("跳过数据导入任务（已禁用）")
            return True
            
    except Exception as e:
        logger.error(f"数据导入任务执行失败: {str(e)}")
        return False

def run_tasks():
    """按顺序执行所有任务"""
    logger.info("开始执行任务序列")
    
    # 执行数据抽取
    if run_data_extraction():
        # 数据抽取成功，执行数据导入
        run_data_import()
    else:
        logger.error("由于数据抽取失败，跳过数据导入任务")

def run_scheduler():
    """运行定时任务"""
    # 从配置文件获取执行间隔和执行时间
    interval = SCHEDULER_CONFIG['EXECUTION_INTERVAL']
    execution_time = SCHEDULER_CONFIG['EXECUTION_TIME']
    
    if interval == 1440:  # 24小时
        # 在指定时间执行
        schedule.every().day.at(execution_time).do(run_tasks)
        logger.info(f"定时任务已启动，将在每天 {execution_time} 执行")
    else:
        # 按指定间隔执行
        schedule.every(interval).minutes.do(run_tasks)
        logger.info(f"定时任务已启动，每 {interval} 分钟执行一次")
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='JIRA数据同步调度器')
    parser.add_argument('--run-now', action='store_true', help='立即执行一次任务')
    args = parser.parse_args()

    if args.run_now:
        logger.info("收到立即执行命令，开始执行任务...")
        run_tasks()
        logger.info("立即执行任务完成")
    else:
        run_scheduler()

if __name__ == "__main__":
    main() 