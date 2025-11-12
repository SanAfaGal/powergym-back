# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the PowerGym Backend API.

## Table of Contents

- [General Troubleshooting](#general-troubleshooting)
- [Installation Issues](#installation-issues)
- [Database Issues](#database-issues)
- [Face Recognition Issues](#face-recognition-issues)
- [Docker Issues](#docker-issues)
- [Environment Variable Issues](#environment-variable-issues)
- [Performance Issues](#performance-issues)
- [Authentication Issues](#authentication-issues)
- [API Issues](#api-issues)
- [Log Analysis](#log-analysis)
- [Getting Help](#getting-help)

## General Troubleshooting

### Check Logs First

Always check logs when encountering issues:

```bash
# Docker
docker compose logs -f backend
docker compose logs -f postgres

# Local
tail -f logs/app.log
```

### Verify Service Status

```bash
# Docker
docker compose ps

# Local
systemctl status powergym  # If using systemd
```

### Health Check

```bash
curl http://localhost:8000/
# Should return: {"message": "API is running", "version": "1.0.0"}
```

## Installation Issues

### Python Version

**Error**: "Python 3.10 or higher is required"

**Solution**:
```bash
python --version  # Check version
# Install Python 3.10+ if needed
```

### Dependency Installation Fails

**Error**: "Failed to install dependencies"

**Solutions**:
1. **Update pip/UV**:
   ```bash
   pip install --upgrade pip
   # Or
   pip install --upgrade uv
   ```

2. **Clear cache**:
   ```bash
   pip cache purge
   ```

3. **Install system dependencies** (for InsightFace):
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install build-essential python3-dev
   ```

### Port Already in Use

**Error**: "Address already in use" or "Port 8000 is already in use"

**Solutions**:
1. **Find process using port**:
   ```bash
   # Linux/Mac
   lsof -i :8000
   
   # Windows
   netstat -ano | findstr :8000
   ```

2. **Kill process**:
   ```bash
   kill <PID>  # Linux/Mac
   taskkill /PID <PID> /F  # Windows
   ```

3. **Change port**:
   ```env
   API_PORT=8001
   ```

## Database Issues

### Connection Refused

**Error**: "Connection refused" or "Could not connect to database"

**Solutions**:
1. **Verify database is running**:
   ```bash
   docker compose ps postgres
   # Or
   systemctl status postgresql
   ```

2. **Check DATABASE_URL**:
   ```bash
   # Docker: Use 'postgres' as hostname
   DATABASE_URL=postgresql://user:pass@postgres:5432/powergym
   
   # Local: Use 'localhost'
   DATABASE_URL=postgresql://user:pass@localhost:5432/powergym
   ```

3. **Test connection**:
   ```bash
   docker compose exec postgres psql -U powergym_user -d powergym
   ```

### Authentication Failed

**Error**: "Password authentication failed"

**Solutions**:
1. **Verify credentials** in `.env`:
   ```env
   POSTGRES_USER=powergym_user
   POSTGRES_PASSWORD=your_password
   ```

2. **Reset password**:
   ```bash
   docker compose exec postgres psql -U postgres
   ALTER USER powergym_user WITH PASSWORD 'new_password';
   ```

### Migration Errors

**Error**: "Target database is not up to date"

**Solutions**:
1. **Check current version**:
   ```bash
   alembic current
   ```

2. **View history**:
   ```bash
   alembic history
   ```

3. **Apply migrations**:
   ```bash
   alembic upgrade head
   ```

4. **If stuck, check migration files**:
   ```bash
   ls -la alembic/versions/
   ```

### pgvector Extension Missing

**Error**: "Extension vector does not exist"

**Solutions**:
1. **Enable extension**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. **Verify installation**:
   ```sql
   \dx vector
   ```

3. **Check PostgreSQL version** (requires 11+):
   ```sql
   SELECT version();
   ```

## Face Recognition Issues

### Model Download Fails

**Error**: "Failed to download InsightFace model"

**Solutions**:
1. **Check internet connection**
2. **Verify disk space**:
   ```bash
   df -h
   ```

3. **Manual download**:
   ```bash
   # Model location
   ~/.insightface/models/buffalo_s/
   ```

### No Face Detected

**Error**: "No face detected in the image"

**Solutions**:
1. **Check image quality**:
   - Minimum 640x640 pixels
   - Good lighting
   - Face clearly visible
   - Frontal angle (within 30 degrees)

2. **Verify image format**:
   - Supported: JPEG, PNG, WebP
   - Check base64 encoding

3. **Test with different image**

### Low Similarity Scores

**Symptoms**: Authentication fails even with correct face

**Solutions**:
1. **Increase tolerance**:
   ```env
   FACE_RECOGNITION_TOLERANCE=0.7
   ```

2. **Re-register face** with better quality image

3. **Check lighting** matches registration conditions

4. **Ensure face angle** is similar to registration

### Model Loading Slow

**Symptoms**: First recognition takes very long

**Solutions**:
1. **Model is cached** after first load
2. **Pre-warm model** on application startup (already implemented)
3. **Use GPU** for faster inference:
   ```env
   INSIGHTFACE_CTX_ID=0
   ```

## Docker Issues

### Container Won't Start

**Error**: Container exits immediately

**Solutions**:
1. **Check logs**:
   ```bash
   docker compose logs backend
   ```

2. **Verify environment variables**:
   ```bash
   docker compose config
   ```

3. **Rebuild container**:
   ```bash
   docker compose up -d --build
   ```

### Database Container Issues

**Error**: Database container keeps restarting

**Solutions**:
1. **Check logs**:
   ```bash
   docker compose logs postgres
   ```

2. **Verify data volume**:
   ```bash
   docker volume ls
   ```

3. **Reset database** (WARNING: Deletes data):
   ```bash
   docker compose down -v
   docker compose up -d
   ```

### Network Issues

**Error**: Containers can't communicate

**Solutions**:
1. **Verify network**:
   ```bash
   docker network ls
   ```

2. **Check service names**:
   - Use `postgres` as hostname in Docker
   - Not `localhost` or `127.0.0.1`

3. **Restart network**:
   ```bash
   docker compose down
   docker compose up -d
   ```

## Environment Variable Issues

### Missing Required Variables

**Error**: "Field required" or "Configuration error"

**Solutions**:
1. **Check .env file exists**:
   ```bash
   ls -la .env
   ```

2. **Verify all required variables**:
   ```bash
   # Required variables
   SECRET_KEY
   BIOMETRIC_ENCRYPTION_KEY
   DATABASE_URL
   SUPER_ADMIN_USERNAME
   SUPER_ADMIN_PASSWORD
   SUPER_ADMIN_EMAIL
   SUPER_ADMIN_FULL_NAME
   EMBEDDING_DIMENSIONS
   ```

3. **Check variable names** (case-sensitive):
   ```env
   SECRET_KEY=...  # Correct
   secret_key=...  # Wrong
   ```

### Invalid Variable Values

**Error**: "Invalid value" or validation error

**Solutions**:
1. **Check data types**:
   - Integers: `API_PORT=8000` (not `"8000"`)
   - Booleans: `DEBUG=false` (not `False` or `0`)
   - Strings: `ENVIRONMENT=production`

2. **Verify formats**:
   - URLs: `DATABASE_URL=postgresql://...`
   - Lists: `ALLOWED_ORIGINS_STR=url1,url2` (comma-separated)

## Performance Issues

### Slow API Responses

**Symptoms**: API takes too long to respond

**Solutions**:
1. **Check database queries**:
   ```sql
   -- Enable query logging
   SET log_statement = 'all';
   ```

2. **Verify indexes**:
   ```sql
   \d+ table_name
   ```

3. **Check connection pool**:
   ```python
   # In app/db/session.py
   pool_size=20
   max_overflow=10
   ```

4. **Monitor resources**:
   ```bash
   docker stats
   ```

### High Memory Usage

**Symptoms**: Container uses too much memory

**Solutions**:
1. **Check memory limits**:
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2.5G
   ```

2. **Review application logs** for memory leaks

3. **Restart container**:
   ```bash
   docker compose restart backend
   ```

### Database Performance

**Symptoms**: Slow database queries

**Solutions**:
1. **Run VACUUM**:
   ```sql
   VACUUM ANALYZE;
   ```

2. **Check indexes**:
   ```sql
   SELECT * FROM pg_indexes WHERE tablename = 'your_table';
   ```

3. **Analyze slow queries**:
   ```sql
   EXPLAIN ANALYZE SELECT ...;
   ```

## Authentication Issues

### Invalid Token

**Error**: "Invalid authentication credentials" or 401 Unauthorized

**Solutions**:
1. **Check token expiration**:
   - Access tokens expire after configured time
   - Use refresh token to get new access token

2. **Verify token format**:
   ```bash
   # Token should start with "Bearer "
   Authorization: Bearer eyJhbGci...
   ```

3. **Check SECRET_KEY**:
   - Must match the key used to sign tokens
   - Changing SECRET_KEY invalidates all tokens

### Token Expired

**Error**: "Token expired"

**Solutions**:
1. **Refresh token**:
   ```http
   POST /api/v1/auth/refresh
   {
     "refresh_token": "..."
   }
   ```

2. **Login again** if refresh token expired

3. **Increase expiration** (development only):
   ```env
   ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
   ```

## API Issues

### 404 Not Found

**Error**: Endpoint not found

**Solutions**:
1. **Check API version**:
   - Use `/api/v1/` prefix
   - Not `/api/` or `/v1/`

2. **Verify endpoint path**:
   - Check Swagger docs: http://localhost:8000/api/v1/docs

3. **Check router registration**:
   - Verify endpoint is registered in `app/api/v1/router.py`

### 422 Validation Error

**Error**: "Unprocessable Entity" with validation details

**Solutions**:
1. **Check request format**:
   - Content-Type: `application/json`
   - Valid JSON syntax

2. **Verify required fields**:
   - Check error details in response
   - All required fields must be provided

3. **Check data types**:
   - Strings, numbers, booleans match schema

### 429 Rate Limit

**Error**: "Rate limit exceeded"

**Solutions**:
1. **Wait** for rate limit to reset
2. **Increase limit** (development):
   ```env
   RATE_LIMIT_PER_MINUTE=200
   ```
3. **Implement retry logic** with exponential backoff

## Log Analysis

### Viewing Logs

```bash
# Docker - All services
docker compose logs -f

# Docker - Specific service
docker compose logs -f backend

# Local - Application logs
tail -f logs/app.log

# Local - Error logs only
tail -f logs/app.log | grep ERROR
```

### Common Log Patterns

#### Database Connection Errors
```
ERROR: Connection refused
ERROR: Password authentication failed
```
→ Check database configuration and credentials

#### Migration Errors
```
ERROR: Target database is not up to date
ERROR: Can't locate revision identified by '...'
```
→ Run `alembic upgrade head`

#### Face Recognition Errors
```
ERROR: No face detected
ERROR: Failed to initialize InsightFace model
```
→ Check image quality and model download

#### Authentication Errors
```
ERROR: Invalid token
ERROR: Token expired
```
→ Refresh token or login again

## Getting Help

### Before Asking for Help

1. **Check logs** for error messages
2. **Review documentation**:
   - [Setup Guide](SETUP.md)
   - [Configuration Guide](CONFIGURATION.md)
   - [Development Guide](DEVELOPMENT.md)

3. **Search existing issues** in the repository

### Information to Provide

When reporting issues, include:

1. **Error message** (full traceback if available)
2. **Environment**:
   - OS and version
   - Python version
   - Docker version (if using)
3. **Configuration** (sanitized):
   - Environment variables (without secrets)
   - Docker Compose configuration
4. **Steps to reproduce**
5. **Logs** (relevant sections)
6. **Expected vs actual behavior**

### Debug Mode

Enable debug mode for more detailed errors:

```env
DEBUG=true
```

**Note**: Only use in development, never in production.

### Common Solutions Summary

| Issue | Quick Fix |
|-------|-----------|
| Database connection failed | Check DATABASE_URL, verify postgres is running |
| Port in use | Change API_PORT or kill process using port |
| Migration error | Run `alembic upgrade head` |
| Face recognition fails | Check image quality, increase tolerance |
| Token expired | Use refresh token or login again |
| Rate limit exceeded | Wait or increase limit (dev only) |
| Container won't start | Check logs, verify .env file |

---

**Next**: [Setup Guide](SETUP.md) | [Configuration Guide](CONFIGURATION.md)

