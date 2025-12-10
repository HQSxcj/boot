#!/bin/bash

# 1. 后台启动 Gunicorn (Python 后端)
# --daemon 让它在后台运行
# --chdir /app/backend 切换到后端代码目录
echo "🚀 Starting Backend (Gunicorn)..."
gunicorn -w 4 -b 127.0.0.1:8000 main:app --chdir /app/backend --daemon

# 2. 前台启动 Nginx
# Nginx 必须在前台运行，否则容器会认为任务结束自动退出
echo "🚀 Starting Frontend (Nginx)..."
nginx -g "daemon off;"
