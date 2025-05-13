#!/bin/bash

# 设置错误时退出
set -e

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    log "错误: Docker未安装"
    exit 1
fi

# 检查磁盘空间
DISK_SPACE=$(df -h . | awk 'NR==2 {print $4}')
log "当前可用磁盘空间: $DISK_SPACE"

# 创建日志目录
mkdir -p logs

# 停止并删除旧容器（如果存在）
log "停止旧容器..."
docker stop jira-sync 2>/dev/null || true
docker rm jira-sync 2>/dev/null || true

# 构建新镜像
log "开始构建新镜像..."
docker build -t jira-sync-scheduler .

# 运行新容器
log "启动新容器..."
docker run -d \
    --name jira-sync \
    --restart unless-stopped \
    -v $(pwd)/logs:/app/logs \
    jira-sync-scheduler

# 等待容器启动
sleep 5

# 检查容器状态
if docker ps | grep -q jira-sync; then
    log "容器启动成功"
    log "容器ID: $(docker ps -q -f name=jira-sync)"
    log "查看日志: docker logs jira-sync"
    log "立即执行: docker exec jira-sync run-now"
else
    log "错误: 容器启动失败"
    docker logs jira-sync
    exit 1
fi 