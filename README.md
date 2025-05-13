# JIRA 数据同步调度器

这是一个用于定时执行 JIRA 数据同步任务的 Docker 应用。它会定期执行数据抽取和导入任务，并将结果保存到数据库中。

## 功能特点

- 支持定时执行数据抽取任务：
  - BugProgress
  - ChangeTracking
  - IterationCompletion
  - SprintPlanning
  - TestCasesAnalyzer
- 支持定时执行数据导入任务：
  - ClearData
  - DatabaseManager
- 可配置的执行间隔
- 完整的日志记录
- Docker 容器化部署
- 支持立即执行功能

## 系统要求

- Docker
- Ubuntu 系统（推荐）
- 至少 1GB 可用内存
- 至少 10GB 可用磁盘空间

## 本地安装步骤

1. 克隆代码仓库：
```bash
git clone <repository-url>
cd <repository-directory>
```

2. 构建 Docker 镜像：
```bash
docker build -t jira-sync-scheduler .
```

3. 运行容器：
```bash
docker run -d \
  --name jira-sync \
  -v $(pwd)/logs:/app/logs \
  jira-sync-scheduler
```

## 云端部署步骤

1. 准备服务器：
```bash
# 安装 Docker（如果尚未安装）
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
```

2. 上传代码：
```bash
# 使用 scp 上传代码（在本地执行）
scp -r /path/to/local/code user@your-server:/path/to/deploy
```

3. 部署应用：
```bash
# 在服务器上执行
cd /path/to/deploy
chmod +x deploy.sh
./deploy.sh
```

4. 验证部署：
```bash
# 检查容器状态
docker ps | grep jira-sync

# 查看日志
docker logs jira-sync
```

## 配置说明

### 配置文件

所有配置都在 `jiraapi/config.py` 文件中：

```python
SCHEDULER_CONFIG = {
    'EXECUTION_INTERVAL': 1440,  # 执行间隔（分钟）
    'EXECUTION_TIME': '08:00',   # 执行时间
    'LOG_LEVEL': 'INFO',         # 日志级别
    'TASKS': {                   # 任务配置
        'DATA_EXTRACTION': {
            'BugProgress': True,
            'ChangeTracking': True,
            ...
        }
    }
}
```

### 日志

- 日志文件位置：`/app/logs/scheduler.log`
- 日志包含：
  - 任务执行时间
  - 执行状态
  - 错误信息（如果有）

## 使用示例

1. 启动定时任务：
```bash
docker run -d --name jira-sync jira-sync-scheduler
```

2. 立即执行一次任务：
```bash
docker exec jira-sync run-now
```

3. 查看日志：
```bash
# 查看容器日志
docker logs jira-sync

# 查看应用日志文件
docker exec jira-sync cat /app/logs/scheduler.log
```

## 维护操作

1. 更新应用：
```bash
# 在服务器上执行
cd /path/to/deploy
git pull  # 如果使用git管理代码
./deploy.sh
```

2. 重启应用：
```bash
docker restart jira-sync
```

3. 停止应用：
```bash
docker stop jira-sync
```

4. 删除应用：
```bash
docker rm -f jira-sync
```

## 故障排除

1. 如果容器无法启动，检查日志：
```bash
docker logs jira-sync
```

2. 如果任务执行失败，检查应用日志：
```bash
docker exec jira-sync cat /app/logs/scheduler.log
```

3. 常见问题：
   - 确保数据库连接配置正确
   - 确保 JIRA API 凭证有效
   - 检查网络连接是否正常
   - 检查磁盘空间是否充足

## 维护说明

- 定期检查日志文件大小
- 监控容器资源使用情况
- 定期更新 Docker 镜像以获取安全补丁
- 定期备份配置文件 