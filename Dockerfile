# ==========================================
# 阶段 1: 构建前端 (使用 Node.js)
# ==========================================
FROM node:18-alpine as frontend-builder
WORKDIR /app-frontend

# 复制前端依赖配置
COPY package.json package-lock.json* ./
# 安装依赖
RUN npm install --legacy-peer-deps

# 复制前端源码 (排除 backend 文件夹，利用 .dockerignore 更好，这里简单处理)
COPY . .
# 删除 backend 目录防止混淆 (可选)
RUN rm -rf backend

# 构建生成 dist 目录
RUN npm run build

# ==========================================
# 阶段 2: 构建最终镜像 (使用 Python + Nginx)
# ==========================================
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 1. 安装系统依赖: Nginx 和 编译工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    gcc \
    libc6-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. 安装 Python 依赖
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir --prefer-binary -r backend/requirements.txt

# 3. 复制后端代码
COPY backend ./backend

# 4. 复制前端构建产物 (从阶段 1 拿过来)
# 将 dist 里面的文件放到 Nginx 默认目录
COPY --from=frontend-builder /app-frontend/dist /usr/share/nginx/html

# 5. 配置 Nginx
# 删除默认配置，换成我们的
RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 6. 复制启动脚本并给权限
COPY start.sh /start.sh
RUN chmod +x /start.sh

# 暴露端口 (只需要 80，8000 是内部通信)
EXPOSE 80

# 启动命令
CMD ["/start.sh"]
