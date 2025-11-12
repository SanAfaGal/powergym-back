# Testing Guide

This guide covers testing strategies, test structure, and best practices for the PowerGym Backend API.

## Table of Contents

- [Testing Overview](#testing-overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Fixtures](#test-fixtures)
- [Mocking Strategies](#mocking-strategies)
- [Test Coverage](#test-coverage)
- [Best Practices](#best-practices)
- [Continuous Integration](#continuous-integration)

## Testing Overview

The PowerGym Backend uses **pytest** for testing with the following approach:

- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test API endpoints and database interactions
- **Repository Tests**: Test data access layer
- **Service Tests**: Test business logic layer

### Test Philosophy

- **Isolation**: Each test is independent
- **Speed**: Tests run quickly using in-memory SQLite
- **Coverage**: Aim for high code coverage
- **Maintainability**: Clear, readable test code

## Test Structure

### Directory Layout

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_user_service.py           # User service tests
├── test_user_repository.py        # User repository tests
├── test_client_service.py         # Client service tests
├── test_client_repository.py      # Client repository tests
├── test_subscription_service.py   # Subscription service tests
├── test_subscription_repository.py # Subscription repository tests
├── test_payment_service.py        # Payment service tests
├── test_plan_service.py           # Plan service tests
├── test_product_service.py       # Product service tests
├── test_attendance_repository.py  # Attendance repository tests
├── test_attendance_service_example.py # Attendance service example
├── test_face_service.py           # Face recognition service tests
├── test_embedding_service.py      # Embedding service tests
└── test_api_face_recognition.py   # Face recognition API tests
```

### Test File Naming

- Test files: `test_*.py`
- Test functions: `test_*`
- Test classes: `Test*`

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_user_service.py

# Run specific test function
pytest tests/test_user_service.py::test_create_user

# Run tests matching pattern
pytest -k "user"

# Run with output
pytest -s
```

### Coverage

```bash
# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Coverage with terminal report
pytest --cov=app --cov-report=term-missing
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

### Filtering Tests

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Writing Tests

### Basic Test Structure

```python
import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate

def test_create_user(db_session):
    """Test creating a new user."""
    # Arrange
    user_data = UserCreate(
        username="testuser",
        email="test@powergym.com",
        password="password123",
        full_name="Test User"
    )
    
    # Act
    user = UserService.create_user(db_session, user_data)
    
    # Assert
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@powergym.com"
```

### Test Organization

#### Arrange-Act-Assert Pattern

```python
def test_example():
    # Arrange: Set up test data and conditions
    data = create_test_data()
    
    # Act: Execute the code being tested
    result = function_under_test(data)
    
    # Assert: Verify the results
    assert result == expected_value
```

### Repository Tests

Test data access layer with mocked database:

```python
from unittest.mock import Mock, MagicMock
from app.repositories.user_repository import UserRepository

def test_create_user():
    # Arrange
    mock_db = Mock()
    mock_user = Mock()
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    repository = UserRepository(mock_db)
    
    # Act
    result = repository.create(mock_user)
    
    # Assert
    assert result == mock_user
    mock_db.add.assert_called_once_with(mock_user)
    mock_db.commit.assert_called_once()
```

### Service Tests

Test business logic with mocked repositories:

```python
from unittest.mock import Mock, patch
from app.services.user_service import UserService

@patch('app.services.user_service.UserRepository')
def test_create_user(mock_repo_class):
    # Arrange
    mock_repo = Mock()
    mock_repo_class.return_value = mock_repo
    mock_user = Mock()
    mock_repo.create.return_value = mock_user
    
    user_data = UserCreate(
        username="testuser",
        email="test@powergym.com",
        password="password123"
    )
    
    # Act
    result = UserService.create_user(Mock(), user_data)
    
    # Assert
    assert result == mock_user
    mock_repo.create.assert_called_once()
```

### API Tests

Test endpoints with FastAPI TestClient:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_login():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "password"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Test Fixtures

### conftest.py

The `conftest.py` file contains shared fixtures:

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from main import app
from app.db.session import get_db

# In-memory SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables before tests, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    """Provide a database session for each test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function", autouse=True)
def override_get_db_fixture(db_session):
    """Override get_db dependency for FastAPI."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client():
    """Provide a test client for API tests."""
    with TestClient(app) as c:
        yield c
```

### Using Fixtures

```python
def test_example(db_session, client):
    # Use db_session for database operations
    # Use client for API requests
    pass
```

### Custom Fixtures

Create custom fixtures in test files:

```python
@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    from app.services.user_service import UserService
    from app.schemas.user import UserCreate
    
    user_data = UserCreate(
        username="testuser",
        email="test@powergym.com",
        password="password123"
    )
    return UserService.create_user(db_session, user_data)
```

## Mocking Strategies

### Mocking Dependencies

```python
from unittest.mock import Mock, patch

@patch('app.services.user_service.UserRepository')
def test_service_method(mock_repo_class):
    # Mock the repository
    mock_repo = Mock()
    mock_repo_class.return_value = mock_repo
    mock_repo.get_by_username.return_value = None
    
    # Test service method
    result = UserService.get_user_by_username(Mock(), "username")
    
    # Verify mock was called
    mock_repo.get_by_username.assert_called_once_with("username")
```

### Mocking External Services

```python
@patch('app.services.notification_service.send_telegram_message')
def test_with_notification(mock_telegram):
    # Mock external service
    mock_telegram.return_value = True
    
    # Test code that uses notification
    result = some_function()
    
    # Verify notification was sent
    mock_telegram.assert_called_once()
```

### Mocking Database

```python
from unittest.mock import Mock

def test_repository_method():
    # Mock database session
    mock_db = Mock()
    mock_query = Mock()
    mock_db.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.first.return_value = None
    
    # Test repository
    repository = UserRepository(mock_db)
    result = repository.get_by_username("username")
    
    # Verify database calls
    mock_db.query.assert_called_once()
```

## Test Coverage

### Coverage Goals

- **Minimum**: 70% overall coverage
- **Target**: 80%+ overall coverage
- **Critical Paths**: 90%+ coverage

### Coverage Reports

```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Generate terminal report
pytest --cov=app --cov-report=term-missing

# Generate XML report (for CI)
pytest --cov=app --cov-report=xml
```

### Coverage Configuration

Create `.coveragerc`:

```ini
[run]
source = app
omit = 
    */tests/*
    */migrations/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

## Best Practices

### 1. Test Naming

Use descriptive test names:

```python
# Good
def test_create_user_with_valid_data_succeeds():
    pass

def test_create_user_with_duplicate_username_fails():
    pass

# Bad
def test_user():
    pass

def test_1():
    pass
```

### 2. Test Isolation

Each test should be independent:

```python
# Good: Each test creates its own data
def test_create_user(db_session):
    user = create_test_user(db_session)
    assert user is not None

def test_get_user(db_session):
    user = create_test_user(db_session)
    result = get_user(db_session, user.id)
    assert result == user

# Bad: Tests depend on each other
def test_create_user():
    global_user = create_user()  # Shared state

def test_get_user():
    result = get_user(global_user.id)  # Depends on previous test
```

### 3. Test Data

Use factories or fixtures for test data:

```python
@pytest.fixture
def user_data():
    return UserCreate(
        username="testuser",
        email="test@powergym.com",
        password="password123"
    )

def test_create_user(db_session, user_data):
    user = UserService.create_user(db_session, user_data)
    assert user.username == user_data.username
```

### 4. Assertions

Use specific assertions:

```python
# Good
assert user.username == "testuser"
assert user.email == "test@example.com"
assert user.is_active is True

# Bad
assert user  # Too generic
```

### 5. Error Testing

Test error cases:

```python
def test_create_user_with_duplicate_username_fails(db_session):
    # Create first user
    user_data = UserCreate(username="testuser", ...)
    UserService.create_user(db_session, user_data)
    
    # Try to create duplicate
    with pytest.raises(ConflictError):
        UserService.create_user(db_session, user_data)
```

### 6. Cleanup

Clean up test data:

```python
def test_example(db_session):
    # Create test data
    user = create_test_user(db_session)
    
    # Test code
    result = some_function(user)
    
    # Cleanup is handled by fixture
    # db_session is rolled back automatically
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install uv
        uv sync
    
    - name: Run tests
      run: |
        pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml
```

### Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.270
    hooks:
      - id: ruff
  
  - repo: local
    hooks:
      - id: tests
        name: tests
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

## Test Examples

### Service Test Example

```python
import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.schemas.user import UserCreate
from app.utils.exceptions import NotFoundError

@patch('app.services.user_service.UserRepository')
def test_create_user_success(mock_repo_class):
    # Arrange
    mock_repo = Mock()
    mock_repo_class.return_value = mock_repo
    mock_user = Mock()
    mock_user.username = "testuser"
    mock_repo.create.return_value = mock_user
    
    user_data = UserCreate(
        username="testuser",
        email="test@powergym.com",
        password="password123"
    )
    
    # Act
    result = UserService.create_user(Mock(), user_data)
    
    # Assert
    assert result.username == "testuser"
    mock_repo.create.assert_called_once()

def test_get_user_not_found(db_session):
    # Arrange
    # No user in database
    
    # Act & Assert
    with pytest.raises(NotFoundError):
        UserService.get_user_by_id(db_session, "nonexistent")
```

### API Test Example

```python
import pytest
from fastapi.testclient import TestClient

def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401

def test_get_current_user(client, sample_user):
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": sample_user.username, "password": "password123"}
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["username"] == sample_user.username
```

---

**Next**: [Development Guide](DEVELOPMENT.md) | [Troubleshooting Guide](TROUBLESHOOTING.md)

