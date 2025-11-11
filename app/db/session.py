"""
Database session management for PowerGym API.

This module provides database connection and session management,
including the SQLAlchemy engine and session factory.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings
from app.core.constants import DEFAULT_DB_POOL_SIZE, DEFAULT_DB_MAX_OVERFLOW

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=DEFAULT_DB_POOL_SIZE,
    max_overflow=DEFAULT_DB_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.

    This function provides a database session that is automatically
    closed after the request is completed. It should be used as a
    FastAPI dependency.

    Yields:
        Database session instance

    Example:
        ```python
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
