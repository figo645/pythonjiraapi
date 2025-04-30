import os
import json

class BaseJira:
    def __init__(self):
        self.JIRA_URL = "https://jira.digitalvolvo.com"
        
        # 从配置文件读取API token
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"请创建配置文件: {config_path}\n格式参考 config.template.json")
            
        with open(config_path, 'r') as f:
            config = json.load(f)
            self.API_TOKEN = config.get('api_token')
            
        if not self.API_TOKEN:
            raise ValueError("配置文件中缺少 api_token")
            
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        # 设置输出目录
        self.OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data') 