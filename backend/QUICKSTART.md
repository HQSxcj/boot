# Quick Start Guide

Get the Flask backend running in under 5 minutes.

## Prerequisites

- Python 3.11 or higher
- pip

## Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run Development Server

```bash
export DATA_PATH=/tmp/appdata.json
python main.py
```

Server will start at `http://localhost:5000`

## Test the API

### 1. Health Check

```bash
curl http://localhost:5000/api/health
```

### 2. First Login (sets up admin password)

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'
```

Save the token from the response.

### 3. Get Config

```bash
curl -X GET http://localhost:5000/api/config \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Update Config

```bash
curl -X PUT http://localhost:5000/api/config \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram": {
      "botToken": "your-bot-token",
      "adminUserId": "12345",
      "whitelistMode": false,
      "notificationChannelId": ""
    },
    ...
  }'
```

## Run Tests

```bash
python -m pytest tests/test_app.py -v
```

## Run Smoke Tests

Start the server in one terminal:

```bash
export DATA_PATH=/tmp/smoke_test.json
python main.py
```

In another terminal:

```bash
pip install requests  # If not already installed
python tests/smoke_test.py
```

## Next Steps

- Read [README.md](README.md) for full API documentation
- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Check [config.example.json](config.example.json) for config structure

## Common Issues

### Port Already in Use

Change the port:

```bash
export PORT=8080
python main.py
```

### Permission Denied on /data

Use a different path:

```bash
export DATA_PATH=$HOME/bot-data.json
python main.py
```

### CORS Errors

Set allowed origins:

```bash
export CORS_ORIGINS=http://localhost:3000,http://localhost:5173
python main.py
```

## Environment Variables

- `DATA_PATH` - Path to JSON data file (default: `/data/appdata.json`)
- `PORT` - Server port (default: `5000`)
- `DEBUG` - Enable debug mode (default: `False`)
- `SECRET_KEY` - Flask secret key (required in production)
- `JWT_SECRET_KEY` - JWT signing key (required in production)
- `CORS_ORIGINS` - Comma-separated allowed origins
