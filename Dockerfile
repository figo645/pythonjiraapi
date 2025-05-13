FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 创建启动脚本
RUN echo '#!/bin/bash\nif [ "$1" = "run-now" ]; then\n    python scheduler.py --run-now\nelse\n    python scheduler.py\nfi' > /app/start.sh && \
    chmod +x /app/start.sh

# 运行应用
ENTRYPOINT ["/app/start.sh"]
CMD [] 