import os
import json
import requests
from .config import API_TOKEN, JIRA_EMAIL

class BaseJira:
    def __init__(self):
        self.JIRA_URL = "https://jira.volvocars.com"
        self.API_TOKEN = API_TOKEN
        self.JIRA_EMAIL = JIRA_EMAIL
        
        if not self.API_TOKEN:
            raise ValueError("配置文件中缺少 API_TOKEN")
            
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_TOKEN}"
        }
        # 设置输出目录
        self.OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data') 