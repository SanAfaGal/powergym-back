# PowerGym Backend API

A comprehensive backend API for gym management systems, featuring facial recognition for attendance tracking, member management, subscriptions, payments, inventory control, and real-time analytics.

## 🚀 Features

### Core Functionality
- **Member Management**: Complete client registration and profile management with biometric data
- **Facial Recognition**: Real-time face recognition for secure and quick check-in using InsightFace
- **Subscription Management**: Flexible membership plans with automatic renewal and payment tracking
- **Payment Processing**: Full and partial payment support with debt tracking
- **Attendance Control**: Automated attendance logging with access validation
- **Inventory Management**: Product and stock control with automated alerts
- **Rewards System**: Attendance-based rewards and promotions
- **Statistics & Reports**: Real-time analytics and comprehensive reporting
- **Telegram Notifications**: Automated notifications for important events

### Technical Features
- **FastAPI**: Modern, high-performance Python web framework
- **PostgreSQL with pgvector**: Vector database for efficient face embedding storage and similarity search
- **JWT Authentication**: Secure token-based authentication
- **Docker Support**: Containerized deployment with Docker Compose
- **Database Migrations**: Alembic for schema versioning
- **Rate Limiting**: Built-in request rate limiting
- **Structured Logging**: Comprehensive logging middleware
- **Error Handling**: Centralized exception handling
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🏃 Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- PostgreSQL 18+ (or use Docker)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd powergym
   ```

2. **Set up environment variables**
   ```bash
   cp docker-compose.example.yml docker-compose.yml
   # Edit .env file with your configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker compose up -d
   ```

4. **Verify installation**
   ```bash
   curl http://localhost:8000/
   # Should return: {"message": "API is running", "version": "1.0.0"}
   ```

5. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md).

## 🛠 Technology Stack

### Backend Framework
- **FastAPI** 0.118+ - Modern Python web framework
- **Uvicorn** - ASGI server
- **Gunicorn** - Production WSGI server

### Database
- **PostgreSQL** 18 - Primary database
- **pgvector** 0.8.1 - Vector extension for face embeddings
- **SQLAlchemy** 2.0+ - ORM
- **Alembic** - Database migrations

### Face Recognition
- **InsightFace** 0.7.3 - Face recognition library
- **ONNX Runtime** 1.15.0 - Model inference
- **OpenCV** 4.11+ - Image processing
- **NumPy** 1.26.4 - Numerical operations

### Authentication & Security
- **PyJWT** - JWT token handling
- **pwdlib** - Password hashing (Argon2)
- **cryptography** - Encryption utilities

### Other Dependencies
- **Pydantic** 2.11+ - Data validation
- **python-telegram-bot** - Telegram notifications
- **slowapi** - Rate limiting
- **httpx** - HTTP client

## 📁 Project Structure

```
powergym/
├── app/
│   ├── api/              # API endpoints and routing
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/             # Core configuration and utilities
│   ├── db/               # Database models and session management
│   ├── middleware/       # Custom middleware (logging, rate limiting, etc.)
│   ├── repositories/    # Data access layer
│   ├── schemas/          # Pydantic schemas for request/response
│   ├── services/         # Business logic layer
│   │   └── face_recognition/  # Face recognition services
│   └── utils/            # Utility functions
├── alembic/              # Database migration scripts
├── tests/                # Test suite
├── scripts/              # Utility scripts (backups, deployment)
├── docs/                 # Documentation
├── logs/                 # Application logs
├── uploads/              # Uploaded files
├── main.py               # Application entry point
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose configuration
├── pyproject.toml        # Project dependencies
└── README.md             # This file
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

### Getting Started
- **[Setup Guide](docs/SETUP.md)** - Installation and initial configuration
- **[Configuration](docs/CONFIGURATION.md)** - Environment variables and settings
- **[Quick Start Backups](docs/QUICK_START_BACKUPS_EN.md)** - Quick backup setup guide

### Development
- **[Development Guide](docs/DEVELOPMENT.md)** - Local development workflow
- **[Testing Guide](docs/TESTING.md)** - Testing strategies and best practices
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture and design patterns

### Deployment & Operations
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Scripts](docs/SCRIPTS.md)** - Deployment and utility scripts
- **[CI/CD](docs/CI_CD.md)** - GitHub Actions and automation
- **[Backup Guide](docs/BACKUP_README_EN.md)** - Database backup and restore

### Features
- **[Face Recognition](docs/FACE_RECOGNITION.md)** - Face recognition system documentation
- **[Rewards System](docs/REWARDS.md)** - Rewards and eligibility system
- **[Notifications](docs/NOTIFICATIONS.md)** - Telegram notification system

### Reference
- **[Database Guide](docs/DATABASE.md)** - Database setup and migrations
- **[API Documentation](docs/API.md)** - API endpoints and usage
- **[Security Policy](docs/SECURITY.md)** - Security policy and best practices
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 💻 Development

### Prerequisites for Development
- Python 3.10+
- UV package manager (recommended) or pip
- PostgreSQL 18+ (or Docker)

### Local Development Setup

1. **Install dependencies**
   ```bash
   # Using UV (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

3. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start development server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

For more details, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_user_service.py
```

See [docs/TESTING.md](docs/TESTING.md) for comprehensive testing documentation.

## 🚢 Deployment

### Production Deployment

1. **Configure production environment**
   ```bash
   cp docker-compose.production.yml docker-compose.yml
   # Update .env with production values
   ```

2. **Build and start services**
   ```bash
   docker compose up -d --build
   ```

3. **Verify deployment**
   ```bash
   docker compose ps
   curl https://your-domain.com/
   ```

For detailed deployment instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## 🔐 Security Considerations

- **Environment Variables**: Never commit `.env` files. Use secure secret management in production.
- **Database**: Use strong passwords and restrict database access.
- **JWT Secrets**: Generate strong, random secret keys.
- **CORS**: Configure allowed origins appropriately for your frontend.
- **Rate Limiting**: Enabled by default to prevent abuse.
- **HTTPS**: Always use HTTPS in production.

## 📊 API Endpoints

The API is organized into the following main categories:

- **Authentication** (`/api/v1/auth`) - Login, logout, token refresh
- **Users** (`/api/v1/users`) - User management
- **Clients** (`/api/v1/clients`) - Client/member management
- **Face Recognition** (`/api/v1/face`) - Face registration and authentication
- **Attendances** (`/api/v1/attendances`) - Attendance tracking
- **Plans** (`/api/v1/plans`) - Membership plans
- **Subscriptions** (`/api/v1/subscriptions`) - Subscription management
- **Payments** (`/api/v1/payments`) - Payment processing
- **Inventory** (`/api/v1/inventory`) - Product and stock management
- **Statistics** (`/api/v1/statistics`) - Analytics and reports
- **Rewards** (`/api/v1/rewards`) - Rewards system

Full API documentation is available at `/api/v1/docs` when the server is running.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 Python style guide
- Use type hints where possible
- Write tests for new features
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory
- **Troubleshooting**: See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
- **Issues**: Open an issue on GitHub

## 📞 Contact

For questions or support, please open an issue in the repository.

---

**Version**: 1.0.0  
**Last Updated**: 2025

