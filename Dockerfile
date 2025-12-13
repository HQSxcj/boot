FROM node:18-alpine as frontend-builder
WORKDIR /app-frontend
COPY package.json package-lock.json* ./
RUN npm config set registry https://registry.npmmirror.com
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends nginx procps dos2unix && rm -rf /var/lib/apt/lists/* && rm -rf /etc/nginx/sites-enabled/default
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt && pip install gunicorn
COPY backend/ .
RUN rm -rf /usr/share/nginx/html/*
COPY --from=frontend-builder /app-frontend/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY start.sh /start.sh
RUN dos2unix /start.sh && chmod +x /start.sh
RUN mkdir -p /data/strm /data/logs
VOLUME ["/data", "/data/strm"]
EXPOSE 18080
CMD ["/start.sh"]