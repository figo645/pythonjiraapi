# Jira API Configuration
API_TOKEN = "MDQ3NDAxMzQ2ODY0OiksiKm1bWeZ1sAfWgqRfQ2WrgPV"
JIRA_EMAIL = "chenfei.xu@volvocars.com"

# Scheduler Configuration
SCHEDULER_CONFIG = {
    # 执行间隔（分钟）
    'EXECUTION_INTERVAL': 1440,  # 默认24小时
    
    # 执行时间（24小时制，格式：HH:MM）
    'EXECUTION_TIME': '08:00',  # 默认早上8点
    
    # 日志配置
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_FILE': 'scheduler.log',
    
    # 任务配置
    'TASKS': {
        'DATA_EXTRACTION': {
            'BugProgress': True,
            'ChangeTracking': True,
            'IterationCompletion': True,
            'SprintPlanning': True,
            'TestCasesAnalyzer': True
        },
        'DATA_IMPORT': {
            'ClearData': True,
            'DatabaseManager': True
        }
    }
} 