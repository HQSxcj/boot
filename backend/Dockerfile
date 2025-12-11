# 使用轻量级 Python 3.12
FROM python:3.12-slim

WORKDIR /app

# 设置环境变量优化 Python 运行
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统级依赖 (编译 C 扩展库如 cryptography/p115client/SQLAlchemy 需要)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖清单
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# 复制后端源码
COPY . .

# 暴露端口
EXPOSE 8000

# 使用 Gunicorn 启动 Flask 应用
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
