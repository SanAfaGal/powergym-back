# Development Guide

This guide covers the development workflow, code structure, and best practices for working with the PowerGym Backend API.

## Table of Contents

- [Development Setup](#development-setup)
- [Code Structure](#code-structure)
- [Architecture Patterns](#architecture-patterns)
- [Development Workflow](#development-workflow)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Debugging](#debugging)
- [Code Style and Best Practices](#code-style-and-best-practices)
- [Common Tasks](#common-tasks)

## Development Setup

If you haven't set up the project yet, follow the [SETUP.md](SETUP.md) guide first.

### Quick Start for Existing Setup

1. **Activate virtual environment**
   ```bash
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate  # Windows
   ```

2. **Start development server**
   ```bash
   uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
   # Or: uvicorn main:app --reload
   ```

The server will automatically reload on code changes.

**Note**: For complete setup instructions, see [SETUP.md](SETUP.md). For configuration details, see [CONFIGURATION.md](CONFIGURATION.md).

## Code Structure

### Directory Organization

```
app/
├── api/                    # API layer
│   ├── dependencies.py     # Shared dependencies (auth, DB session)
│   └── v1/
│       ├── router.py       # Main API router
│       └── endpoints/      # Endpoint modules
│           ├── auth.py
│           ├── users.py
│           ├── clients.py
│           └── ...
│
├── core/                   # Core configuration
│   ├── config.py          # Settings and configuration
│   ├── security.py        # Authentication and encryption
│   └── constants.py      # Application constants
│
├── db/                     # Database layer
│   ├── base.py            # Base model class
│   ├── models.py          # SQLAlchemy models
│   └── session.py        # Database session management
│
├── middleware/             # Custom middleware
│   ├── logging.py         # Structured logging
│   ├── rate_limit.py      # Rate limiting
│   ├── compression.py     # Response compression
│   └── error_handler.py   # Exception handling
│
├── repositories/           # Data access layer
│   ├── base_repository.py # Base repository class
│   ├── user_repository.py
│   ├── client_repository.py
│   └── ...
│
├── schemas/                # Pydantic schemas
│   ├── user.py
│   ├── client.py
│   └── ...
│
├── services/               # Business logic layer
│   ├── user_service.py
│   ├── client_service.py
│   ├── face_recognition/   # Face recognition services
│   │   ├── core.py
│   │   ├── embedding.py
│   │   └── database.py
│   └── ...
│
└── utils/                    # Utility functions
    ├── exceptions.py       # Custom exceptions
    ├── response.py        # Response helpers
    └── ...
```

### Layer Responsibilities

1. **API Layer** (`app/api/`)
   - Handles HTTP requests/responses
   - Request validation using Pydantic schemas
   - Authentication and authorization
   - Calls service layer

2. **Service Layer** (`app/services/`)
   - Business logic
   - Data transformation
   - Orchestrates repository calls
   - Handles notifications

3. **Repository Layer** (`app/repositories/`)
   - Database operations
   - Query building
   - Data persistence
   - No business logic

4. **Schema Layer** (`app/schemas/`)
   - Request/response validation
   - Data serialization
   - Type safety

## Architecture Patterns

### Repository Pattern

Repositories abstract database operations:

```python
# app/repositories/user_repository.py
class UserRepository(BaseRepository[UserModel, str]):
    def get_by_username(self, username: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(
            UserModel.username == username
        ).first()
```

### Service Pattern

Services contain business logic:

```python
# app/services/user_service.py
class UserService:
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserModel:
        # Business logic here
        hashed_password = hash_password(user_data.password)
        user = UserModel(**user_data.dict(), hashed_password=hashed_password)
        return UserRepository(db).create(user)
```

### Dependency Injection

FastAPI's dependency injection is used throughout:

```python
# app/api/dependencies.py
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserModel:
    # Authentication logic
    return user
```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow code style guidelines
   - Write tests for new features
   - Update documentation

3. **Run tests**
   ```bash
   pytest
   ```

4. **Check code style**
   ```bash
   # If using black
   black app/
   
   # If using ruff
   ruff check app/
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Hot Reload

The development server automatically reloads on file changes:

```bash
uvicorn main:app --reload
```

Changes to Python files will trigger a reload. For database migrations, restart the server.

### Database Changes

When modifying models:

1. **Update the model** in `app/db/models.py`
2. **Create a migration**
   ```bash
   alembic revision --autogenerate -m "description of changes"
   ```
3. **Review the migration** in `alembic/versions/`
4. **Apply the migration**
   ```bash
   alembic upgrade head
   ```

See [DATABASE.md](DATABASE.md) for detailed migration guide.

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "add new column to users"

# Create empty migration for manual changes
alembic revision -m "custom migration"
```

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

### Migration Best Practices

1. **Always review auto-generated migrations** before applying
2. **Test migrations** on a copy of production data
3. **Use transactions** for data migrations
4. **Never edit applied migrations** - create new ones instead
5. **Document breaking changes** in migration comments

## Testing

See [TESTING.md](TESTING.md) for comprehensive testing documentation.

### Quick Test Commands

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_user_service.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_user_service.py::test_create_user

# Run with verbose output
pytest -v
```

### Test Structure

Tests mirror the application structure:

```
tests/
├── conftest.py           # Pytest fixtures
├── test_user_service.py
├── test_client_service.py
└── ...
```

## Debugging

### Using Python Debugger

Add breakpoints in your code:

```python
import pdb; pdb.set_trace()
```

Or use the debugger in your IDE (VS Code, PyCharm, etc.).

### Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Processing request", extra={"user_id": user_id})
logger.error("Error occurred", exc_info=True)
```

View logs:

```bash
# Docker
docker compose logs -f backend

# Local
tail -f logs/app.log
```

### Debug Mode

Enable debug mode in `.env`:

```env
DEBUG=true
```

This provides:
- Detailed error messages
- Stack traces
- Request/response logging

### Database Debugging

Access the database:

```bash
# Docker
docker compose exec postgres psql -U powergym_user -d powergym

# Local
psql -U powergym_user -d powergym
```

Or use Adminer (development only):
- URL: http://localhost:8080
- Server: `postgres`
- Username: From `.env`
- Password: From `.env`
- Database: `powergym`

## Code Style and Best Practices

### Python Style Guide

Follow PEP 8 with these guidelines:

1. **Type Hints**: Use type hints for all function parameters and return values
   ```python
   def get_user(db: Session, user_id: int) -> Optional[UserModel]:
       ...
   ```

2. **Docstrings**: Document public functions and classes
   ```python
   def create_client(db: Session, client_data: ClientCreate) -> ClientModel:
       """
       Create a new client.
       
       Args:
           db: Database session
           client_data: Client creation data
           
       Returns:
           Created client model
       """
   ```

3. **Naming Conventions**:
   - Classes: `PascalCase` (e.g., `UserService`)
   - Functions/Variables: `snake_case` (e.g., `get_user`)
   - Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`)

4. **Imports**: Organize imports
   ```python
   # Standard library
   from typing import Optional, List
   
   # Third-party
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   
   # Local
   from app.services.user_service import UserService
   ```

### Error Handling

Use custom exceptions:

```python
from app.utils.exceptions import NotFoundError, ValidationError

if not user:
    raise NotFoundError("User not found")

if not email_valid:
    raise ValidationError("Invalid email format")
```

### Response Formatting

Use consistent response formats:

```python
from app.utils.response import success_response, error_response

return success_response(data=user, message="User created")
return error_response(message="User not found", status_code=404)
```

## Common Tasks

### Adding a New Endpoint

1. **Create schema** in `app/schemas/`
   ```python
   class ItemCreate(BaseModel):
       name: str
       price: float
   ```

2. **Create repository** in `app/repositories/` (if needed)
   ```python
   class ItemRepository(BaseRepository[ItemModel, UUID]):
       ...
   ```

3. **Create service** in `app/services/`
   ```python
   class ItemService:
       @staticmethod
       def create_item(db: Session, item_data: ItemCreate) -> ItemModel:
           ...
   ```

4. **Create endpoint** in `app/api/v1/endpoints/`
   ```python
   @router.post("/items", response_model=Item)
   def create_item(
       item: ItemCreate,
       db: Session = Depends(get_db),
       current_user: UserModel = Depends(get_current_user)
   ):
       return ItemService.create_item(db, item)
   ```

5. **Register router** in `app/api/v1/router.py`
   ```python
   from app.api.v1.endpoints import items
   api_router.include_router(items.router, prefix="/items", tags=["items"])
   ```

### Adding a New Model

1. **Define model** in `app/db/models.py`
   ```python
   class ItemModel(Base):
       __tablename__ = "items"
       id = Column(UUID, primary_key=True, default=uuid.uuid4)
       name = Column(String, nullable=False)
   ```

2. **Create migration**
   ```bash
   alembic revision --autogenerate -m "add items table"
   ```

3. **Review and apply migration**
   ```bash
   alembic upgrade head
   ```

### Adding Middleware

Create middleware in `app/middleware/`:

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Pre-processing
        response = await call_next(request)
        # Post-processing
        return response
```

Register in `main.py`:

```python
app.add_middleware(CustomMiddleware)
```

## Development Tools

### Recommended IDE Setup

- **VS Code**:
  - Python extension
  - Pylance for type checking
  - Python Test Explorer
  - Docker extension

- **PyCharm**:
  - Professional edition recommended
  - Built-in database tools
  - Docker integration

### Useful Commands

```bash
# Format code (if using black)
black app/

# Lint code (if using ruff)
ruff check app/
ruff format app/

# Type checking (if using mypy)
mypy app/

# Run specific migration
alembic upgrade <revision>

# Check migration status
alembic current
alembic history

# View API docs
# http://localhost:8000/api/v1/docs
```

## Troubleshooting Development Issues

### Import Errors

If you get import errors:

1. Ensure virtual environment is activated
2. Verify dependencies are installed: `pip list` or `uv pip list`
3. Check Python path: `python -c "import sys; print(sys.path)"`

### Database Connection Issues

1. Verify PostgreSQL is running
2. Check `DATABASE_URL` in `.env`
3. Test connection:
   ```python
   from app.db.session import engine
   engine.connect()
   ```

### Migration Issues

1. Check current migration: `alembic current`
2. View migration history: `alembic history`
3. If stuck, check migration files in `alembic/versions/`

### Port Already in Use

Change port in `.env`:
```env
API_PORT=8001
```

Or kill the process:
```bash
# Find process
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill process
kill <PID>
```

---

**Next**: [Testing Guide](TESTING.md) | [API Documentation](API.md)

