# PowerGym Backend API

![FastAPI](https://img.shields.io/badge/FastAPI-0.118+-005571?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18+-316192?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)

A comprehensive gym management system backend with facial recognition, member management, subscriptions, payments, and real-time analytics.

## Features

- **Authentication & Authorization** - JWT-based authentication with role-based access control (Admin, Employee)
- **Face Recognition** - Real-time facial recognition for secure check-in using InsightFace
- **Attendance Management** - Track member attendance with automatic entry/exit logging
- **Client Management** - Complete client registration and profile management
- **Subscription Management** - Flexible membership plans with automatic renewal tracking
- **Payment System** - Track payments, debts, and transaction history
- **Inventory Management** - Product and stock control with movement tracking
- **Statistics & Reports** - Comprehensive analytics and reporting system
- **Rewards System** - Attendance-based rewards and incentives
- **Telegram Notifications** - Automated notifications via Telegram bot

## Tech Stack

### Core Technologies
- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.10+** - Programming language
- **PostgreSQL 18+** - Relational database with pgvector extension for vector operations
- **Alembic** - Database migration tool

### Key Libraries
- **InsightFace** - Face recognition and embedding extraction
- **SQLAlchemy** - ORM for database operations
- **Pydantic** - Data validation and settings management
- **JWT** - JSON Web Token authentication
- **pgvector** - Vector similarity search for face embeddings
- **Uvicorn** - ASGI server

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 18+ with pgvector extension
- Docker & Docker Compose (optional, for containerized deployment)

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd powergym
```

### 2. Install dependencies

This project uses `uv` for dependency management:

```bash
# Install uv if you don't have it
pip install uv

# Install project dependencies
uv sync
```

### 3. Environment setup

Create a `.env` file in the root directory or copy from `docker-compose.example.yml`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/powergym
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=powergym
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Security
SECRET_KEY=your-secret-key-here
BIOMETRIC_ENCRYPTION_KEY=your-encryption-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=300  # 5 horas
REFRESH_TOKEN_EXPIRE_HOURS=12  # 12 horas (sesión máxima)

# Super Admin (created on startup)
SUPER_ADMIN_USERNAME=admin
SUPER_ADMIN_PASSWORD=admin123
SUPER_ADMIN_EMAIL=admin@powergym.com
SUPER_ADMIN_FULL_NAME=Super Admin

# Face Recognition
EMBEDDING_DIMENSIONS=512
INSIGHTFACE_MODEL=buffalo_l
FACE_RECOGNITION_TOLERANCE=0.6

# CORS
ALLOWED_ORIGINS_STR=http://localhost:5173

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
TELEGRAM_ENABLED=true
```

### 4. Database setup

Ensure PostgreSQL is running and create the database:

```bash
# Create database
createdb powergym

# Or using psql
psql -U postgres -c "CREATE DATABASE powergym;"
```

The pgvector extension will be automatically enabled via init scripts when using Docker, or you can enable it manually:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 5. Run migrations

```bash
# Activate virtual environment (if using uv)
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run migrations
alembic upgrade head
```

### 6. Start the server

```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using uv
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## Configuration

### Environment Variables

Key environment variables are defined in `app/core/config.py`. The application supports:

- **Environment-specific configs**: `.env`, `.env.development`, `.env.production`
- **Priority**: `ENV_FILE` env var > `.env` > `.env.{ENVIRONMENT}`

### Key Settings

- **Database**: PostgreSQL connection strings (sync and async)
- **Security**: JWT secret keys, token expiration, encryption keys
- **Face Recognition**: Model selection, tolerance, embedding dimensions
- **CORS**: Allowed origins for cross-origin requests
- **Rate Limiting**: Request throttling configuration
- **Telegram**: Bot token and chat ID for notifications

## Usage

### Running Locally

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start development server
uvicorn main:app --reload
```

### Running with Docker

```bash
# Build the image
docker build -t powergym-backend:latest .

# Run the container
docker run -p 8000:8000 --env-file .env powergym-backend:latest
```

### Running with Docker Compose

```bash
# Copy example compose file
cp docker-compose.example.yml docker-compose.yml

# Edit docker-compose.yml with your settings
# Then start services
docker-compose up -d
```

### Deploy from Production

To apply changes from production to your Docker server, use the deploy script:

```bash
./deploy.sh
```

**Options:**
- `--no-cache`: Force rebuild without using Docker cache (slower but ensures clean build)
- `--branch BRANCH`: Specify branch to pull from (default: current branch)

**Examples:**
```bash
# Standard deploy (uses cache for faster builds)
./deploy.sh

# Deploy with clean rebuild (no cache)
./deploy.sh --no-cache

# Deploy from specific branch
./deploy.sh --branch main
```

The script automatically:
1. Verifies prerequisites (git, docker, docker-compose)
2. Fetches the latest changes from the repository (`git pull`)
3. Stops the current containers gracefully
4. Rebuilds the backend image (using Docker cache by default for speed)
5. Restarts the containers
6. Shows the backend logs

**Note:** Make sure the script has execute permissions:
```bash
chmod +x deploy.sh
```

**Alternative script (rebuild only):**
If you already have local changes and only need to rebuild containers without pulling:

```bash
# Standard rebuild (uses cache)
./rebuild.sh

# Rebuild without cache
./rebuild.sh --no-cache
```

This script skips the `git pull` step and only rebuilds and restarts the containers. It's useful for testing local changes quickly.

### API Endpoints

- **Base URL**: `http://localhost:8000/api/v1`
- **Health Check**: `GET /health`
- **API Docs**: `http://localhost:8000/api/v1/openapi.json`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)

### Authentication

1. Login to get access token:
   ```bash
   POST /api/v1/auth/login
   {
     "username": "admin",
     "password": "admin123"
   }
   ```

2. Use token in subsequent requests:
   ```bash
   Authorization: Bearer <access_token>
   ```

## Project Structure

```
powergym/
├── app/
│   ├── api/              # API endpoints and routing
│   │   └── v1/
│   │       └── endpoints/  # Individual endpoint modules
│   ├── core/             # Core configuration and utilities
│   ├── db/               # Database models and session
│   ├── middleware/       # Custom middleware (logging, compression, rate limiting)
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic models for request/response
│   ├── services/         # Business logic layer
│   │   └── face_recognition/  # Face recognition service
│   └── utils/            # Utility functions
├── alembic/              # Database migrations
├── tests/                # Test suite
├── init-scripts/         # Database initialization scripts
├── main.py               # Application entry point
├── pyproject.toml        # Project dependencies
└── Dockerfile            # Docker image configuration
```

## API Documentation

The API follows RESTful principles and includes:

- **Authentication**: `/api/v1/auth/*`
- **Users**: `/api/v1/users/*`
- **Clients**: `/api/v1/clients/*`
- **Face Recognition**: `/api/v1/face/*`
- **Attendances**: `/api/v1/attendances/*`
- **Plans**: `/api/v1/plans/*`
- **Subscriptions**: `/api/v1/subscriptions/*`
- **Payments**: `/api/v1/payments/*`
- **Inventory**: `/api/v1/inventory/*`
- **Statistics**: `/api/v1/statistics/*`
- **Rewards**: `/api/v1/rewards/*`

Full API documentation is available via Swagger UI at `/docs` when the server is running.

## Development

### Running Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/
```

### Code Style

The project follows PEP 8 Python style guidelines. Consider using:
- `black` for code formatting
- `flake8` or `ruff` for linting
- `mypy` for type checking

## Docker

### Build Image

```bash
docker build -t powergym-backend:latest .
```

The Dockerfile includes:
- Python 3.10 base image
- System dependencies for OpenCV and InsightFace
- Pre-downloaded InsightFace model (buffalo_l)
- Application code and dependencies

### Docker Compose

The `docker-compose.example.yml` includes:
- **PostgreSQL** with pgvector extension (port 5432)
- **Backend API** (port 8000)
- **Adminer** (optional, port 8080) for database administration

### Volumes

- `postgres_data`: Persistent database storage
- `./logs`: Application logs
- `./uploads`: User-uploaded files

## Automated Tasks

### Expiración Automática de Subscripciones

El sistema incluye un workflow de GitHub Actions que expira automáticamente las subscripciones que han finalizado. Este workflow se ejecuta diariamente a las 00:00 hora de Bogotá.

**Configuración:**
1. Ve a `.github/workflows/README.md` para instrucciones detalladas
2. Configura los secrets `API_BASE_URL` y `API_TOKEN` en GitHub
3. El workflow se ejecutará automáticamente según el schedule configurado

**Endpoint:**
- `POST /api/v1/subscriptions/expire` - Expira todas las subscripciones que han finalizado

Para más información, consulta la [documentación completa de GitHub Actions](.github/workflows/README.md).

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

For more information, visit the [API Documentation](http://localhost:8000/docs) when the server is running.

