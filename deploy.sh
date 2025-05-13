#!/bin/bash

# 停止并删除旧容器（如果存在）
docker stop jira-sync 2>/dev/null
docker rm jira-sync 2>/dev/null

# 构建新镜像
docker build -t jira-sync-scheduler .

# 运行新容器
docker run -d \
    --name jira-sync \
    --restart unless-stopped \
    -v $(pwd)/logs:/app/logs \
    jira-sync-scheduler

# 显示容器状态
docker ps | grep jira-sync 