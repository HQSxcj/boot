#!/bin/bash

# 1. 启动 Gunicorn (Python 后端)
# 修改点 A: 去掉了 --chdir /app/backend (因为代码就在当前目录 /app)
# 修改点 B: 改为 "main:create_app()" (调用工厂函数)
# 修改点 C: 增加了日志输出到文件，方便排查错误 (--access-logfile - --error-logfile -)
echo "🚀 Starting Backend (Gunicorn)..."

gunicorn -w 4 -b 127.0.0.1:8000 "main:create_app()" --daemon \
    --access-logfile - \
    --error-logfile /var/log/gunicorn_error.log

# 稍微等待一下，检查 Gunicorn 是否存活
sleep 2
if pgrep gunicorn > /dev/null; then
    echo "✅ Gunicorn started successfully."
else
    echo "❌ Gunicorn failed to start! Checking logs:"
    cat /var/log/gunicorn_error.log
    exit 1
fi

# 2. 前台启动 Nginx
echo "🚀 Starting Frontend (Nginx)..."
nginx -g "daemon off;"