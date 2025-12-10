# Deployment Guide

This guide provides instructions for deploying the Flask backend in various environments.

## Quick Start (Development)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set up environment
export DATA_PATH=/tmp/appdata.json
export DEBUG=True

# Run server
python main.py
```

The server will start on `http://localhost:5000`

## Production Deployment

### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required
SECRET_KEY=your-random-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars
DATA_PATH=/data/appdata.json

# Optional
PORT=5000
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DEBUG=False
```

### Using Gunicorn (Recommended)

```bash
# Install gunicorn (included in requirements.txt)
pip install -r requirements.txt

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 "main:create_app()"

# Or with more options
gunicorn \
  --workers 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile /var/log/gunicorn/access.log \
  --error-logfile /var/log/gunicorn/error.log \
  "main:create_app()"
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /data

# Set environment variables
ENV DATA_PATH=/data/appdata.json
ENV PORT=5000

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:create_app()"]
```

Build and run:

```bash
docker build -t 115-bot-backend .
docker run -d \
  -p 5000:5000 \
  -v /path/to/data:/data \
  -e SECRET_KEY=your-secret-key \
  -e JWT_SECRET_KEY=your-jwt-secret \
  -e CORS_ORIGINS=https://yourdomain.com \
  --name bot-backend \
  115-bot-backend
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    volumes:
      - ./data:/data
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATA_PATH=/data/appdata.json
      - CORS_ORIGINS=https://yourdomain.com
    restart: unless-stopped
```

Run:

```bash
docker-compose up -d
```

### Systemd Service

Create `/etc/systemd/system/bot-backend.service`:

```ini
[Unit]
Description=115 Telegram Bot Backend
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/bot-backend
Environment="DATA_PATH=/var/lib/bot/appdata.json"
Environment="SECRET_KEY=your-secret-key"
Environment="JWT_SECRET_KEY=your-jwt-secret"
Environment="CORS_ORIGINS=https://yourdomain.com"
ExecStart=/opt/bot-backend/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 "main:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable bot-backend
sudo systemctl start bot-backend
sudo systemctl status bot-backend
```

### Nginx Reverse Proxy

Add to Nginx configuration:

```nginx
upstream backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /api/health {
        proxy_pass http://backend;
        access_log off;
    }
}
```

Test and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Security Checklist

- [ ] Generate strong random keys for `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Set proper `CORS_ORIGINS` to your frontend domain(s)
- [ ] Use HTTPS in production (never plain HTTP)
- [ ] Set proper file permissions on data directory (chmod 700)
- [ ] Enable firewall rules to restrict access
- [ ] Set up log rotation for gunicorn logs
- [ ] Monitor rate limiting and adjust as needed
- [ ] Enable 2FA for admin account
- [ ] Regular backups of `/data/appdata.json`
- [ ] Keep dependencies updated

## Monitoring

### Health Check

```bash
curl https://api.yourdomain.com/api/health
```

### Logs

```bash
# Systemd service
sudo journalctl -u bot-backend -f

# Docker
docker logs -f bot-backend

# Gunicorn
tail -f /var/log/gunicorn/error.log
tail -f /var/log/gunicorn/access.log
```

## Backup and Restore

### Backup

```bash
# Backup data file
cp /data/appdata.json /backup/appdata-$(date +%Y%m%d).json

# Or with Docker
docker cp bot-backend:/data/appdata.json /backup/appdata-$(date +%Y%m%d).json
```

### Restore

```bash
# Restore data file
cp /backup/appdata-20240101.json /data/appdata.json

# Or with Docker
docker cp /backup/appdata-20240101.json bot-backend:/data/appdata.json
docker restart bot-backend
```

## Troubleshooting

### Port already in use

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>
```

### Permission denied on /data

```bash
# Fix permissions
sudo chown -R www-data:www-data /data
sudo chmod 700 /data
```

### CORS errors

Ensure `CORS_ORIGINS` includes your frontend URL:

```bash
export CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### JWT token expired

Tokens are valid for 24 hours. Client needs to re-login.

### Cannot connect to backend

1. Check if service is running
2. Check firewall rules
3. Verify network connectivity
4. Check logs for errors

## Performance Tuning

### Gunicorn Workers

Formula: `(2 x CPU cores) + 1`

```bash
# For 2 CPU cores
gunicorn -w 5 -b 0.0.0.0:5000 "main:create_app()"
```

### Rate Limiting

Adjust in `main.py`:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["500 per day", "100 per hour"],  # Adjust as needed
    storage_uri="memory://"
)
```

For distributed deployment, use Redis:

```python
storage_uri="redis://localhost:6379"
```

## Upgrading

```bash
# Backup data
cp /data/appdata.json /backup/appdata-backup.json

# Stop service
sudo systemctl stop bot-backend

# Update code
cd /opt/bot-backend
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Start service
sudo systemctl start bot-backend

# Verify
curl http://localhost:5000/api/health
```
