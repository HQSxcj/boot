# 115 Telegram Bot Admin - Backend API

Production-ready Flask backend for the 115 Telegram Bot Admin application.

## Features

- **App Factory Pattern**: Clean `create_app()` factory for easy testing and configuration
- **JWT Authentication**: Token-based authentication with 24-hour expiry
- **2FA Support**: TOTP-based two-factor authentication with QR code provisioning
- **Rate Limiting**: 5 login attempts per minute, 50 requests per hour globally
- **CORS Support**: Configurable cross-origin resource sharing for SPA
- **Persistence Layer**: JSON-based data store with thread-safe operations
- **Comprehensive Tests**: Unit tests for all endpoints and data operations

## Project Structure

```
backend/
├── main.py                 # App factory and entry point
├── blueprints/            # API route blueprints
│   ├── auth.py           # Authentication endpoints
│   ├── config.py         # Configuration management
│   └── health.py         # Health check
├── middleware/           # Custom middleware
│   └── auth.py          # JWT authentication decorator
├── persistence/         # Data storage layer
│   └── store.py        # JSON-based data store
├── models/             # Data models (for future expansion)
├── tests/              # Unit tests
│   └── test_app.py    # Comprehensive test suite
└── requirements.txt    # Python dependencies
```

## Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Environment variables:

- `SECRET_KEY`: Flask secret key (default: `dev-secret-key-change-in-production`)
- `JWT_SECRET_KEY`: JWT signing key (default: `jwt-secret-key-change-in-production`)
- `DATA_PATH`: Path to JSON data file (default: `/data/appdata.json`)
- `CORS_ORIGINS`: Comma-separated list of allowed origins (default: `http://localhost:5173,http://localhost:3000`)
- `PORT`: Server port (default: `5000`)
- `DEBUG`: Enable debug mode (default: `False`)

## Running the Server

### Development

```bash
export DATA_PATH=/tmp/appdata.json
export DEBUG=True
python main.py
```

### Production

```bash
export SECRET_KEY=your-secure-secret-key
export JWT_SECRET_KEY=your-secure-jwt-key
export DATA_PATH=/data/appdata.json
export CORS_ORIGINS=https://yourdomain.com
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

Or use the app factory:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "main:create_app()"
```

## API Endpoints

### Health Check

**GET** `/api/health`

Returns service health status.

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "115-telegram-bot-admin",
    "version": "1.0.0"
  }
}
```

### Authentication

#### Login

**POST** `/api/auth/login`

Authenticate user and receive JWT token.

```json
// Request
{
  "username": "admin",
  "password": "yourpassword"
}

// Response
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "username": "admin",
    "requires2FA": false
  }
}
```

**Rate Limit**: 5 requests per minute

#### Verify OTP

**POST** `/api/auth/verify-otp`

Verify two-factor authentication code.

```json
// Request (requires Authorization header)
{
  "code": "123456"
}

// Response
{
  "success": true,
  "data": {
    "verified": true
  }
}
```

#### Setup 2FA

**POST** `/api/auth/setup-2fa`

Generate and store a new 2FA secret.

```json
// Response (requires Authorization header)
{
  "success": true,
  "data": {
    "secret": "JBSWY3DPEHPK3PXP",
    "qrCodeUri": "otpauth://totp/admin?secret=JBSWY3DPEHPK3PXP&issuer=115%20Telegram%20Bot"
  }
}
```

#### Get Current User

**GET** `/api/auth/me` or **GET** `/api/me`

Get current user information.

```json
// Response (requires Authorization header)
{
  "success": true,
  "data": {
    "username": "admin",
    "twoFactorEnabled": false
  }
}
```

### Configuration

#### Get Configuration

**GET** `/api/config`

Retrieve full application configuration.

```json
// Response (requires Authorization header)
{
  "success": true,
  "data": {
    "telegram": {
      "botToken": "",
      "adminUserId": "",
      "whitelistMode": false,
      "notificationChannelId": ""
    },
    "cloud115": { ... },
    "cloud123": { ... },
    // ... other config sections
  }
}
```

#### Update Configuration

**PUT** `/api/config`

Update application configuration.

```json
// Request (requires Authorization header)
{
  "telegram": {
    "botToken": "your-token",
    "adminUserId": "12345",
    ...
  },
  // ... other config sections
}

// Response
{
  "success": true,
  "data": { ... } // Updated configuration
}
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

Tokens are valid for 24 hours after issuance.

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error message description"
}
```

Common status codes:
- `400` - Bad request (missing required fields)
- `401` - Unauthorized (invalid or missing token)
- `404` - Not found
- `500` - Internal server error

## Testing

Run the test suite:

```bash
python -m pytest tests/test_app.py -v
```

Run with coverage:

```bash
python -m pytest tests/test_app.py --cov=. --cov-report=html
```

## Data Storage

The application uses a JSON file for data persistence with the following structure:

```json
{
  "admin": {
    "username": "admin",
    "password_hash": "...",
    "two_factor_secret": "...",
    "two_factor_enabled": false
  },
  "config": {
    // Full AppConfig structure
  }
}
```

The data file is created automatically on first run with default values.

## Security Considerations

1. **Change default secrets**: Always set `SECRET_KEY` and `JWT_SECRET_KEY` in production
2. **Use HTTPS**: Never expose the API over plain HTTP in production
3. **Rate limiting**: Built-in rate limiting protects against brute force attacks
4. **Password hashing**: Passwords are hashed using Werkzeug's secure methods
5. **2FA**: Enable two-factor authentication for enhanced security
6. **CORS**: Configure `CORS_ORIGINS` to only allow trusted domains

## Docker Deployment

The backend is designed to run in a Docker container. See the main project README for Docker deployment instructions.

## Development

To extend the API:

1. Create new blueprints in `blueprints/` directory
2. Register blueprints in `main.py` `create_app()` function
3. Add middleware decorators as needed (`@require_auth`)
4. Write tests in `tests/` directory

## License

See main project LICENSE file.
