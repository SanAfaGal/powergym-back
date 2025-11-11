import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from main import app
from app.db.session import get_db

# ⚙️ Base de datos en memoria para pruebas
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Fixture que crea las tablas antes de los tests
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# ✅ Fixture para obtener una sesión de base de datos de prueba
@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Sobrescribimos get_db correctamente para FastAPI
@pytest.fixture(scope="function", autouse=True)
def override_get_db_fixture(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

# ✅ Cliente de prueba
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
