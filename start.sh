#!/bin/bash

set -e

echo "================================================"
echo "🚀 Boot 服务启动中..."
echo "================================================"

# 0. 确保数据目录存在并设置权限
echo "📁 检查数据目录..."
mkdir -p /data/strm /data/logs
chmod -R 755 /data

# 检查 /data 目录的写入权限
if [ ! -w /data ]; then
    echo "⚠️  警告: /data 目录无写入权限，尝试修复权限..."
    chmod -R 755 /data || {
        echo "❌ 无法修复 /data 权限！"
        echo "请确保 Docker 容器有足够权限访问挂载的数据卷"
        echo "提示: 检查宿主机上 /your/data 目录的权限"
        exit 1
    }
fi

# 初始化配置文件（如果不存在）
if [ ! -f /data/config.yml ]; then
    echo "📋 初始化配置文件..."
    cat > /data/config.yml << 'EOF'
telegram:
  botToken: ''
  adminUserId: ''
  whitelistMode: true
  notificationChannelId: ''
cloud115:
  loginMethod: cookie
  loginApp: web
  cookies: ''
  userAgent: ''
  downloadPath: ''
  downloadDirName: ''
  autoDeleteMsg: false
  qps: 1
cloud123:
  enabled: false
  clientId: ''
  clientSecret: ''
  downloadPath: ''
  downloadDirName: ''
  autoDeleteMsg: false
  qps: 1
emby:
  enabled: false
  baseUrl: ''
  apiKey: ''
  mediaLibraryNames: []
strm:
  enabled: false
  outputDir: ''
  webdavUrl: ''
  webdavPort: 8080
  webdavPath: ''
  concurrency: 5
EOF
    echo "✅ 配置文件已创建: /data/config.yml"
    echo "⚠️  请启动后通过 Web UI (http://localhost:18080) 进行配置"
fi

# 1. 检查前端文件是否存在
echo "📦 检查前端静态文件..."
if [ -f /usr/share/nginx/html/index.html ]; then
    echo "✅ 前端文件存在"
else
    echo "❌ 前端文件缺失！"
    echo "创建占位页面..."
    mkdir -p /usr/share/nginx/html
    echo "<html><body><h1>前端构建失败</h1><p>请检查 Docker 构建日志</p></body></html>" > /usr/share/nginx/html/index.html
fi

# 2. 检查 nginx 配置
echo "🔧 检查 Nginx 配置..."
nginx -t

# 2.5. 初始化数据库（防止 Gunicorn worker 竞态条件）
echo "💾 初始化数据库..."
cd /app
python << 'PYEOF' 2>&1 || echo "⚠️  数据库初始化完成或有非致命警告"
try:
    from models.database import init_all_databases
    init_all_databases()
    print("✅ 数据库初始化完成")
except Exception as e:
    print(f"⚠️  数据库初始化注意: {e}")
    # 不退出，因为表可能已存在
PYEOF

# 3. 启动 Gunicorn (Python 后端)
echo "🐍 启动后端服务 (Gunicorn)..."
cd /app
gunicorn -w 4 -b 127.0.0.1:8000 "main:create_app()" --daemon \
    --access-logfile /data/logs/gunicorn_access.log \
    --error-logfile /data/logs/gunicorn_error.log \
    --capture-output 2>&1 || {
    echo "❌ 后端服务启动失败！"
    echo "--- 错误信息 ---"
    cat /data/logs/gunicorn_error.log 2>/dev/null || echo "无日志记录"
    exit 1
}

# 等待并检查 Gunicorn 是否存活
sleep 3
if pgrep gunicorn > /dev/null; then
    echo "✅ 后端服务启动成功 (PID: $(pgrep gunicorn))"
else
    echo "❌ 后端服务启动失败！"
    echo "--- Gunicorn 错误日志 ---"
    tail -20 /data/logs/gunicorn_error.log 2>/dev/null || echo "无日志"
    exit 1
fi

# 4. 启动 Nginx (前台)
echo "🌐 启动前端服务 (Nginx)..."
echo "================================================"
echo "✅ Boot 服务启动完成"
echo "📱 Web UI: http://localhost:18080"
echo "================================================"
echo "✅ 服务启动完成！访问 http://localhost:18080"
echo "================================================"
nginx -g "daemon off;"