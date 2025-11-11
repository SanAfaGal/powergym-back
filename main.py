"""
PowerGym Backend API Application.

This is the main FastAPI application entry point that sets up the API,
configures middleware, and handles application lifecycle events.
"""

import logging
import warnings
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import SessionLocal
from app.middleware.compression import CompressionMiddleware
from app.middleware.error_handler import setup_exception_handlers
from app.middleware.logging import StructuredLoggingMiddleware
from app.middleware.rate_limit import setup_rate_limiting
from app.services.user_service import UserService

# Suppress pkg_resources deprecation warnings
warnings.filterwarnings('ignore', message='pkg_resources is deprecated')

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.
    
    Handles startup and shutdown logic for the FastAPI application.
    On startup, initializes the super admin user if needed.
    
    Args:
        app: FastAPI application instance
        
    Yields:
        None (control returns to application)
    """
    # Startup
    logger.info("Starting PowerGym API application")
    db = SessionLocal()
    try:
        logger.info("Initializing super admin user")
        UserService.initialize_super_admin(db)
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Error during application startup: {e}", exc_info=True)
        raise
    finally:
        db.close()
    
    yield
    
    # Shutdown
    logger.info("Shutting down PowerGym API application")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    description="PowerGym Backend API for gym management and face recognition"
)

# Add middleware in order of execution (last added = first executed)
app.add_middleware(StructuredLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.ENABLE_COMPRESSION:
    app.add_middleware(CompressionMiddleware, minimum_size=1000)

# Setup exception handlers and rate limiting
setup_exception_handlers(app)
setup_rate_limiting(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root() -> dict:
    """
    Root endpoint providing API information.
    
    Returns:
        Dictionary with API status and version
    """
    return {"message": "API is running", "version": settings.VERSION}
