# Configuration Guide

This guide explains all configuration options available in the PowerGym Backend API.

## Table of Contents

- [Configuration Overview](#configuration-overview)
- [Environment Variables](#environment-variables)
  - [Application Configuration](#application-configuration)
  - [Security Settings](#security-settings)
  - [Database Configuration](#database-configuration)
  - [Face Recognition Settings](#face-recognition-settings)
  - [Image Processing](#image-processing)
  - [CORS and Origins](#cors-and-origins)
  - [Super Admin](#super-admin)
  - [Telegram Notifications](#telegram-notifications)
  - [Rate Limiting](#rate-limiting)
- [Configuration Files](#configuration-files)
- [Best Practices](#best-practices)
- [Environment-Specific Configurations](#environment-specific-configurations)

## Configuration Overview

The PowerGym Backend uses **Pydantic Settings** to manage configuration. Settings are loaded from:

1. Environment variables (highest priority)
2. `.env` file in the project root
3. `.env.{ENVIRONMENT}` file (e.g., `.env.development`, `.env.production`)
4. Default values (if defined)

Configuration is defined in `app/core/config.py` and accessed via `app.core.config.settings`.

## Environment Variables

### Application Configuration

#### `PROJECT_NAME`
- **Type**: String
- **Default**: `"PowerGym API"`
- **Description**: Name of the application
- **Example**: `PROJECT_NAME=PowerGym API`

#### `VERSION`
- **Type**: String
- **Default**: `"1.0.0"`
- **Description**: Application version
- **Example**: `VERSION=1.0.0`

#### `API_V1_STR`
- **Type**: String
- **Default**: `"/api/v1"`
- **Description**: API version prefix for all endpoints
- **Example**: `API_V1_STR=/api/v1`

#### `DEBUG`
- **Type**: Boolean
- **Default**: `False`
- **Description**: Enable debug mode (shows detailed error messages)
- **Example**: `DEBUG=true`
- **Note**: Should be `False` in production

#### `ENVIRONMENT`
- **Type**: String
- **Default**: `"development"`
- **Description**: Current environment (development, staging, production)
- **Example**: `ENVIRONMENT=production`
- **Values**: `development`, `staging`, `production`

### Security Settings

#### `SECRET_KEY`
- **Type**: String
- **Required**: Yes
- **Description**: Secret key for JWT token signing and encryption
- **Example**: `SECRET_KEY=your-very-secure-random-string-here`
- **Generation**:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  # Or
  openssl rand -hex 32
  ```
- **Security**: Must be a strong, random string. Never commit to version control.

#### `ALGORITHM`
- **Type**: String
- **Default**: `"HS256"`
- **Description**: JWT signing algorithm
- **Example**: `ALGORITHM=HS256`
- **Note**: Typically should remain `HS256`

#### `ACCESS_TOKEN_EXPIRE_MINUTES`
- **Type**: Integer
- **Default**: `300` (5 hours)
- **Description**: Access token expiration time in minutes
- **Example**: `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- **Recommendation**: 
  - Development: 480-1440 (8-24 hours)
  - Production: 60-300 (1-5 hours)

#### `REFRESH_TOKEN_EXPIRE_HOURS`
- **Type**: Integer
- **Default**: `12`
- **Description**: Refresh token expiration time in hours
- **Example**: `REFRESH_TOKEN_EXPIRE_HOURS=24`
- **Recommendation**: 12-168 hours (1 week max)

#### `BIOMETRIC_ENCRYPTION_KEY`
- **Type**: String
- **Required**: Yes
- **Description**: Encryption key for biometric data (face embeddings)
- **Example**: `BIOMETRIC_ENCRYPTION_KEY=your-encryption-key-here`
- **Generation**: Same as `SECRET_KEY`
- **Security**: Must be 32+ characters. Never commit to version control.

### Database Configuration

#### `DATABASE_URL`
- **Type**: String (PostgreSQL connection URL)
- **Required**: Yes
- **Description**: Full database connection string
- **Format**: `postgresql://[user]:[password]@[host]:[port]/[database]`
- **Examples**:
  - Docker: `DATABASE_URL=postgresql://user:pass@postgres:5432/powergym`
  - Local: `DATABASE_URL=postgresql://user:pass@localhost:5432/powergym`
  - Remote: `DATABASE_URL=postgresql://user:pass@db.your-domain.com:5432/powergym`

#### `POSTGRES_USER`
- **Type**: String
- **Optional**: Yes (if using DATABASE_URL)
- **Description**: PostgreSQL username
- **Example**: `POSTGRES_USER=powergym_user`

#### `POSTGRES_PASSWORD`
- **Type**: String
- **Optional**: Yes (if using DATABASE_URL)
- **Description**: PostgreSQL password
- **Example**: `POSTGRES_PASSWORD=secure_password_123`
- **Security**: Use strong passwords in production

#### `POSTGRES_DB`
- **Type**: String
- **Optional**: Yes (if using DATABASE_URL)
- **Description**: PostgreSQL database name
- **Example**: `POSTGRES_DB=powergym`

#### `POSTGRES_HOST`
- **Type**: String
- **Optional**: Yes (if using DATABASE_URL)
- **Description**: PostgreSQL host
- **Example**: 
  - Docker: `POSTGRES_HOST=postgres`
  - Local: `POSTGRES_HOST=localhost`

#### `POSTGRES_PORT`
- **Type**: Integer
- **Optional**: Yes (if using DATABASE_URL)
- **Default**: `5432`
- **Description**: PostgreSQL port
- **Example**: `POSTGRES_PORT=5432`

### Face Recognition Settings

#### `EMBEDDING_DIMENSIONS`
- **Type**: Integer
- **Required**: Yes
- **Default**: `512`
- **Description**: Dimension of face embeddings (InsightFace buffalo_s uses 512)
- **Example**: `EMBEDDING_DIMENSIONS=512`
- **Note**: Must match the model being used

#### `INSIGHTFACE_MODEL`
- **Type**: String
- **Default**: `"buffalo_s"`
- **Description**: InsightFace model name
- **Example**: `INSIGHTFACE_MODEL=buffalo_s`
- **Options**: 
  - `buffalo_s` - Smaller, faster (recommended)
  - `buffalo_l` - Larger, more accurate
- **Note**: Model is downloaded automatically on first use

#### `INSIGHTFACE_DET_SIZE`
- **Type**: Integer
- **Default**: `640`
- **Description**: Face detection size in pixels
- **Example**: `INSIGHTFACE_DET_SIZE=640`
- **Recommendation**: 640 for most cases, 1280 for higher accuracy

#### `INSIGHTFACE_CTX_ID`
- **Type**: Integer
- **Default**: `-1`
- **Description**: Context ID for GPU (-1 for CPU, 0+ for GPU)
- **Example**: 
  - CPU: `INSIGHTFACE_CTX_ID=-1`
  - GPU: `INSIGHTFACE_CTX_ID=0`
- **Note**: Requires CUDA and appropriate drivers for GPU

#### `FACE_RECOGNITION_TOLERANCE`
- **Type**: Float
- **Default**: `0.6`
- **Description**: Similarity threshold for face matching (0.0-1.0)
- **Example**: `FACE_RECOGNITION_TOLERANCE=0.6`
- **Guidelines**:
  - Lower (0.4-0.5): More strict, fewer false positives
  - Higher (0.7-0.8): More lenient, more false positives
  - Recommended: 0.6 for balanced accuracy

### Image Processing

#### `MAX_IMAGE_SIZE_MB`
- **Type**: Integer
- **Default**: `5`
- **Description**: Maximum image size in megabytes
- **Example**: `MAX_IMAGE_SIZE_MB=10`
- **Recommendation**: 5-10 MB for face recognition

#### `ALLOWED_IMAGE_FORMATS_STR`
- **Type**: String (comma-separated)
- **Default**: `"jpg,jpeg,png,webp"`
- **Description**: Allowed image formats
- **Example**: `ALLOWED_IMAGE_FORMATS_STR=jpg,jpeg,png,webp,bmp`
- **Note**: Parsed into a list automatically

#### `IMAGE_COMPRESSION_QUALITY`
- **Type**: Integer
- **Default**: `85`
- **Range**: 1-100
- **Description**: JPEG compression quality for stored images
- **Example**: `IMAGE_COMPRESSION_QUALITY=90`
- **Recommendation**: 85-95 for good quality/size balance

#### `THUMBNAIL_COMPRESSION_QUALITY`
- **Type**: Integer
- **Default**: `70`
- **Range**: 1-100
- **Description**: JPEG compression quality for thumbnails
- **Example**: `THUMBNAIL_COMPRESSION_QUALITY=75`

#### `THUMBNAIL_WIDTH`
- **Type**: Integer
- **Default**: `150`
- **Description**: Thumbnail width in pixels
- **Example**: `THUMBNAIL_WIDTH=200`

#### `THUMBNAIL_HEIGHT`
- **Type**: Integer
- **Default**: `150`
- **Description**: Thumbnail height in pixels
- **Example**: `THUMBNAIL_HEIGHT=200`

#### `EMBEDDING_COMPRESSION_LEVEL`
- **Type**: Integer
- **Default**: `9`
- **Range**: 0-9
- **Description**: Compression level for stored embeddings (0=no compression, 9=max)
- **Example**: `EMBEDDING_COMPRESSION_LEVEL=9`
- **Note**: Higher compression saves space but uses more CPU

#### `ENABLE_COMPRESSION`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable image compression
- **Example**: `ENABLE_COMPRESSION=true`

### CORS and Origins

#### `ALLOWED_ORIGINS_STR`
- **Type**: String (comma-separated)
- **Default**: `"http://localhost:5173"`
- **Description**: Allowed CORS origins (comma-separated)
- **Example**: `ALLOWED_ORIGINS_STR=http://localhost:5173,https://app.your-domain.com`
- **Format**: Comma-separated URLs without spaces
- **Security**: Only include trusted frontend URLs

### Super Admin

These settings create the initial super admin user on first startup.

#### `SUPER_ADMIN_USERNAME`
- **Type**: String
- **Required**: Yes
- **Description**: Initial admin username
- **Example**: `SUPER_ADMIN_USERNAME=admin`
- **Security**: Change default value in production

#### `SUPER_ADMIN_PASSWORD`
- **Type**: String
- **Required**: Yes
- **Description**: Initial admin password
- **Example**: `SUPER_ADMIN_PASSWORD=change_this_immediately`
- **Security**: Must be changed after first login in production

#### `SUPER_ADMIN_EMAIL`
- **Type**: String (email format)
- **Required**: Yes
- **Description**: Initial admin email
- **Example**: `SUPER_ADMIN_EMAIL=admin@powergym.com`

#### `SUPER_ADMIN_FULL_NAME`
- **Type**: String
- **Required**: Yes
- **Description**: Initial admin full name
- **Example**: `SUPER_ADMIN_FULL_NAME=Administrator`

### Telegram Notifications

#### `TELEGRAM_BOT_TOKEN`
- **Type**: String
- **Optional**: Yes
- **Description**: Telegram bot token from @BotFather
- **Example**: `TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
- **Setup**: 
  1. Message @BotFather on Telegram
  2. Use `/newbot` command
  3. Follow instructions to get token

#### `TELEGRAM_CHAT_ID`
- **Type**: String
- **Optional**: Yes
- **Description**: Telegram chat ID for notifications
- **Example**: `TELEGRAM_CHAT_ID=123456789`
- **How to get**: 
  1. Message your bot
  2. Visit: `https://api.telegram.org/bot<TOKEN>/getUpdates`
  3. Find `chat.id` in the response

#### `TELEGRAM_ENABLED`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable Telegram notifications
- **Example**: `TELEGRAM_ENABLED=true`

### Rate Limiting

#### `RATE_LIMIT_ENABLED`
- **Type**: Boolean
- **Default**: `True`
- **Description**: Enable rate limiting
- **Example**: `RATE_LIMIT_ENABLED=true`

#### `RATE_LIMIT_PER_MINUTE`
- **Type**: Integer
- **Default**: `60`
- **Description**: Maximum requests per minute per IP
- **Example**: `RATE_LIMIT_PER_MINUTE=100`
- **Recommendation**: 
  - Development: 100-200
  - Production: 60-100

### Admin UI

#### `ADMINER_PORT`
- **Type**: Integer
- **Optional**: Yes
- **Description**: Port for Adminer database UI (development only)
- **Example**: `ADMINER_PORT=8080`
- **Note**: Should not be exposed in production

## Configuration Files

### .env File Structure

Create a `.env` file in the project root:

```env
# Application
ENVIRONMENT=development
DEBUG=false

# Security
SECRET_KEY=your-secret-key-here
BIOMETRIC_ENCRYPTION_KEY=your-encryption-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=300
REFRESH_TOKEN_EXPIRE_HOURS=12

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/powergym

# Face Recognition
EMBEDDING_DIMENSIONS=512
INSIGHTFACE_MODEL=buffalo_s
FACE_RECOGNITION_TOLERANCE=0.6

# CORS
ALLOWED_ORIGINS_STR=http://localhost:5173

# Super Admin
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_PASSWORD=change_this
SUPER_ADMIN_EMAIL=admin@powergym.com
SUPER_ADMIN_FULL_NAME=Administrator

# Telegram (Optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TELEGRAM_ENABLED=false
```

### Environment-Specific Files

You can create environment-specific files:

- `.env.development` - Development settings
- `.env.staging` - Staging settings
- `.env.production` - Production settings

The application will load `.env.{ENVIRONMENT}` based on the `ENVIRONMENT` variable.

## Best Practices

### Security

1. **Never commit `.env` files** to version control
2. **Use strong, random secrets** for `SECRET_KEY` and `BIOMETRIC_ENCRYPTION_KEY`
3. **Change default admin credentials** immediately
4. **Use different secrets** for each environment
5. **Restrict CORS origins** to only trusted frontend URLs
6. **Use environment variables** in production, not `.env` files

### Performance

1. **Adjust rate limits** based on expected traffic
2. **Optimize image compression** based on storage/quality needs
3. **Use GPU** for face recognition if available (`INSIGHTFACE_CTX_ID=0`)
4. **Tune face recognition tolerance** based on accuracy requirements

### Development vs Production

**Development:**
- `DEBUG=true`
- Longer token expiration
- Higher rate limits
- Adminer enabled

**Production:**
- `DEBUG=false`
- Shorter token expiration
- Lower rate limits
- Adminer disabled
- Strong secrets
- Restricted CORS

## Environment-Specific Configurations

### Development

```env
ENVIRONMENT=development
DEBUG=true
ACCESS_TOKEN_EXPIRE_MINUTES=1440
RATE_LIMIT_PER_MINUTE=200
ALLOWED_ORIGINS_STR=http://localhost:5173,http://localhost:3000
```

### Production

```env
ENVIRONMENT=production
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=60
RATE_LIMIT_PER_MINUTE=60
ALLOWED_ORIGINS_STR=https://app.your-domain.com
TELEGRAM_ENABLED=true
```

### Staging

```env
ENVIRONMENT=staging
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=300
RATE_LIMIT_PER_MINUTE=100
ALLOWED_ORIGINS_STR=https://staging.your-domain.com
```

## Verifying Configuration

### Check Loaded Settings

```python
from app.core.config import settings

print(f"Environment: {settings.ENVIRONMENT}")
print(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'Not set'}")
print(f"Debug: {settings.DEBUG}")
```

### Validate Configuration

The application will fail to start if required variables are missing. Check logs:

```bash
docker compose logs backend | grep -i "error\|missing\|required"
```

---

**Next**: [Development Guide](DEVELOPMENT.md) | [Deployment Guide](DEPLOYMENT.md)

