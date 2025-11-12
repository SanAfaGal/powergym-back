# Setup Guide

This guide will walk you through setting up the PowerGym Backend API from scratch.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [Docker Compose (Recommended)](#docker-compose-recommended)
  - [Local Development Setup](#local-development-setup)
- [Initial Configuration](#initial-configuration)
- [Verification](#verification)
- [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Python 3.10 or higher**
  - Check version: `python --version` or `python3 --version`
  - Download: [python.org](https://www.python.org/downloads/)

- **Docker and Docker Compose**
  - Docker Desktop: [docker.com](https://www.docker.com/products/docker-desktop)
  - Verify installation:
    ```bash
    docker --version
    docker compose version
    ```

- **Git**
  - Download: [git-scm.com](https://git-scm.com/downloads)
  - Verify: `git --version`

### Optional but Recommended

- **UV Package Manager** (faster than pip)
  - Install: `pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Verify: `uv --version`

- **PostgreSQL Client Tools** (for direct database access)
  - Included with PostgreSQL or Docker

## Installation Methods

### Docker Compose (Recommended)

This is the easiest and recommended method for getting started quickly.

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd powergym
```

#### Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file (if available)
cp .env.example .env

# Or create manually
touch .env
```

Edit `.env` with the following required variables:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@postgres:5432/powergym
POSTGRES_USER=powergym_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=powergym
POSTGRES_PORT=5432

# Security
SECRET_KEY=your-secret-key-here-generate-a-random-string
BIOMETRIC_ENCRYPTION_KEY=your-biometric-encryption-key-here

# Super Admin (created on first startup)
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_PASSWORD=change_this_password
SUPER_ADMIN_EMAIL=admin@powergym.com
SUPER_ADMIN_FULL_NAME=Administrator

# Face Recognition
EMBEDDING_DIMENSIONS=512
INSIGHTFACE_MODEL=buffalo_s
FACE_RECOGNITION_TOLERANCE=0.6

# Application
ENVIRONMENT=development
ALLOWED_ORIGINS_STR=http://localhost:5173,http://localhost:3000

# Optional: Telegram Notifications
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_ENABLED=true
```

**Important**: Generate secure random strings for `SECRET_KEY` and `BIOMETRIC_ENCRYPTION_KEY`:

```bash
# On Linux/Mac
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use openssl
openssl rand -hex 32
```

#### Step 3: Start Services

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Check service status
docker compose ps
```

#### Step 4: Wait for Services to Initialize

The backend will automatically:
1. Wait for the database to be ready
2. Run database migrations
3. Initialize the super admin user
4. Pre-load the face recognition model

This may take 1-2 minutes on first startup. Monitor the logs:

```bash
docker compose logs -f backend
```

You should see:
```
Database is ready!
Running database migrations...
Application startup completed successfully
```

### Local Development Setup

For local development without Docker:

#### Step 1: Clone and Navigate

```bash
git clone <repository-url>
cd powergym
```

#### Step 2: Set Up Python Environment

**Using UV (Recommended):**

```bash
# Install UV if not already installed
pip install uv

# Sync dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

**Using pip:**

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

#### Step 3: Set Up PostgreSQL Database

**Option A: Using Docker (Easiest)**

```bash
# Start only PostgreSQL
docker run -d \
  --name powergym_db \
  -e POSTGRES_USER=powergym_user \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=powergym \
  -p 5432:5432 \
  pgvector/pgvector:0.8.1-pg18-trixie
```

**Option B: Local PostgreSQL Installation**

1. Install PostgreSQL 18+ with pgvector extension
2. Create database:
   ```sql
   CREATE DATABASE powergym;
   CREATE EXTENSION vector;
   ```

#### Step 4: Configure Environment

Create `.env` file with required variables. See [CONFIGURATION.md](CONFIGURATION.md) for complete details.

**Minimum required variables:**
```env
DATABASE_URL=postgresql://powergym_user:password@localhost:5432/powergym
SECRET_KEY=your-secret-key-here
BIOMETRIC_ENCRYPTION_KEY=your-encryption-key-here
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_PASSWORD=change_this_password
SUPER_ADMIN_EMAIL=admin@powergym.com
SUPER_ADMIN_FULL_NAME=Administrator
EMBEDDING_DIMENSIONS=512
ENVIRONMENT=development
ALLOWED_ORIGINS_STR=http://localhost:5173
```

**Note**: Generate secure random strings for `SECRET_KEY` and `BIOMETRIC_ENCRYPTION_KEY`. See [CONFIGURATION.md](CONFIGURATION.md) for details.

#### Step 5: Run Migrations

```bash
# Using UV
uv run alembic upgrade head

# Or using pip
alembic upgrade head
```

#### Step 6: Start the Application

```bash
# Development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using UV
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Initial Configuration

### 1. Verify Database Connection

Check that the database is accessible:

```bash
# With Docker
docker compose exec backend python -c "from app.db.session import engine; print('Connected!' if engine.connect() else 'Failed')"

# Local
python -c "from app.db.session import engine; engine.connect(); print('Connected!')"
```

### 2. Verify Super Admin Creation

The super admin user is created automatically on first startup. You can verify by:

- Logging in via the API:
  ```bash
  curl -X POST http://localhost:8000/api/v1/auth/token \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin&password=your_admin_password"
  ```

- Or checking the database:
  ```sql
  SELECT username, email, role FROM users WHERE username = 'admin';
  ```

### 3. Access API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Verification

### Health Check

Test that the API is running:

```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "message": "API is running",
  "version": "1.0.0"
}
```

### Test Authentication

Test the login endpoint:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_admin_password"
  }'
```

Expected response:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "refresh_token": "eyJ..."
}
```

### Check Database Tables

Verify that all tables were created:

```bash
# With Docker
docker compose exec postgres psql -U powergym_user -d powergym -c "\dt"

# Local
psql -U powergym_user -d powergym -c "\dt"
```

You should see tables like: `users`, `clients`, `subscriptions`, `attendances`, `biometrics`, etc.

### Verify Face Recognition Model

The InsightFace model should be downloaded automatically on first use. Check logs for:

```
InsightFace model warmed up successfully
```

Or verify the model directory:

```bash
# With Docker
docker compose exec backend ls -la /root/.insightface/models/

# Local
ls -la ~/.insightface/models/
```

## Next Steps

Now that your setup is complete:

1. **Read the Configuration Guide**: See [CONFIGURATION.md](CONFIGURATION.md) for detailed configuration options
2. **Explore the API**: Visit http://localhost:8000/api/v1/docs
3. **Set Up Development**: See [DEVELOPMENT.md](DEVELOPMENT.md) for development workflow
4. **Learn About Face Recognition**: See [FACE_RECOGNITION.md](FACE_RECOGNITION.md)
5. **Review Database Setup**: See [DATABASE.md](DATABASE.md)

## Troubleshooting

If you encounter issues during setup:

1. **Check Logs**
   ```bash
   docker compose logs backend
   docker compose logs postgres
   ```

2. **Verify Environment Variables**
   ```bash
   docker compose exec backend env | grep -E "(DATABASE|SECRET|ADMIN)"
   ```

3. **Check Database Connection**
   ```bash
   docker compose exec postgres pg_isready -U powergym_user
   ```

4. **Restart Services**
   ```bash
   docker compose restart
   ```

For more troubleshooting help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

## Common Issues

### Port Already in Use

If port 8000 is already in use:

```bash
# Change API_PORT in .env
API_PORT=8001

# Restart services
docker compose down
docker compose up -d
```

### Database Connection Failed

Ensure:
- Database container is running: `docker compose ps`
- DATABASE_URL uses correct hostname (`postgres` in Docker, `localhost` locally)
- Credentials match in `.env` and database

### Migration Errors

If migrations fail:

```bash
# Check current migration status
docker compose exec backend alembic current

# Reset and re-run (WARNING: This will delete data)
docker compose exec backend alembic downgrade base
docker compose exec backend alembic upgrade head
```

---

**Next**: [Configuration Guide](CONFIGURATION.md)

