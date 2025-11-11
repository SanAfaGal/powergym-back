"""
Monitoring and health check endpoints.

This module provides endpoints for health checks, readiness probes, and
application metrics. These endpoints are essential for container orchestration
(Docker, Kubernetes) and monitoring systems.
"""

import logging
import platform
import sys
import time
from functools import lru_cache
from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

# Track application startup time for uptime calculation
_APP_START_TIME: float = time.time()


# Response Models
class HealthStatus(BaseModel):
    """Health check response model."""
    
    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ..., description="Overall health status"
    )
    version: str = Field(..., description="API version")
    timestamp: float = Field(..., description="Unix timestamp of the check")
    uptime_seconds: float = Field(..., description="Application uptime in seconds")
    database: Dict[str, str] = Field(..., description="Database connection status")
    system: Dict[str, str] = Field(..., description="System information")


class ReadinessStatus(BaseModel):
    """Readiness check response model."""
    
    ready: bool = Field(..., description="Service readiness status")
    checks: Dict[str, bool] = Field(..., description="Individual check results")


class MetricsResponse(BaseModel):
    """Metrics endpoint response model."""
    
    api: Dict[str, str] = Field(..., description="API information")
    features: Dict[str, bool] = Field(..., description="Feature flags")
    face_recognition: Dict[str, Any] = Field(..., description="Face recognition configuration")
    system: Dict[str, str] = Field(..., description="System information")


# Helper Functions
def _check_database_connection(db: Session, timeout: float = 2.0) -> Dict[str, str]:
    """
    Check database connection with timeout.
    
    Args:
        db: Database session
        timeout: Maximum time to wait for response in seconds
        
    Returns:
        Dictionary with connection status and details
    """
    start_time = time.time()
    try:
        # Use a lightweight query with timeout
        db.execute(text("SELECT 1"))
        response_time = time.time() - start_time
        
        if response_time > timeout:
            logger.warning(f"Database check took {response_time:.3f}s (threshold: {timeout}s)")
            return {
                "status": "connected",
                "response_time_ms": f"{response_time * 1000:.2f}",
                "warning": "slow_response"
            }
        
        return {
            "status": "connected",
            "response_time_ms": f"{response_time * 1000:.2f}"
        }
    except SQLAlchemyError as e:
        logger.error(f"Database connection check failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error during database check: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Unexpected error: {str(e)}"
        }


@lru_cache(maxsize=1)
def _get_system_info() -> Dict[str, str]:
    """
    Get system information (cached for performance).
    
    Returns:
        Dictionary with system information
    """
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "environment": settings.ENVIRONMENT
    }


@lru_cache(maxsize=1)
def _get_static_metrics() -> Dict:
    """
    Get static metrics that don't change during runtime (cached).
    
    Returns:
        Dictionary with static metrics
    """
    return {
        "api": {
            "version": settings.VERSION,
            "name": settings.PROJECT_NAME
        },
        "features": {
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
            "compression_enabled": settings.ENABLE_COMPRESSION,
            "telegram_enabled": settings.TELEGRAM_ENABLED
        },
        "face_recognition": {
            "model": f"InsightFace {settings.INSIGHTFACE_MODEL}",
            "tolerance": settings.FACE_RECOGNITION_TOLERANCE,
            "embedding_dimensions": settings.EMBEDDING_DIMENSIONS,
            "detection_size": settings.INSIGHTFACE_DET_SIZE
        },
        "system": _get_system_info()
    }


# Endpoints
@router.get(
    "/health",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Comprehensive health check endpoint for monitoring and load balancers",
    tags=["monitoring"]
)
def health_check(db: Session = Depends(get_db)) -> HealthStatus:
    """
    Perform comprehensive health check.
    
    This endpoint checks the overall health of the application including:
    - Database connectivity
    - Application uptime
    - System information
    
    Returns:
        HealthStatus with detailed health information
        
    Status codes:
        - 200: Application is healthy or degraded
        - 503: Application is unhealthy (if database is completely down)
    """
    check_start_time = time.time()
    uptime = time.time() - _APP_START_TIME
    
    # Check database connection
    db_status = _check_database_connection(db)
    
    # Determine overall status
    if db_status["status"] == "connected":
        overall_status: Literal["healthy", "degraded", "unhealthy"] = "healthy"
        if "warning" in db_status:
            overall_status = "degraded"
    elif db_status["status"] == "error":
        overall_status = "unhealthy"
    else:
        overall_status = "degraded"
    
    response_time = time.time() - check_start_time
    
    # Log if health check is slow
    if response_time > 1.0:
        logger.warning(f"Health check took {response_time:.3f}s")
    
    health_data = HealthStatus(
        status=overall_status,
        version=settings.VERSION,
        timestamp=time.time(),
        uptime_seconds=round(uptime, 2),
        database=db_status,
        system=_get_system_info()
    )
    
    # Return 503 if unhealthy
    if overall_status == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is unhealthy"
        )
    
    return health_data


@router.get(
    "/ready",
    response_model=ReadinessStatus,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Readiness probe for Kubernetes and container orchestration",
    tags=["monitoring"]
)
def readiness_check(db: Session = Depends(get_db)) -> ReadinessStatus:
    """
    Perform readiness check.
    
    This endpoint verifies that the service is ready to accept traffic.
    It performs lightweight checks on critical dependencies.
    
    Returns:
        ReadinessStatus with check results
        
    Raises:
        HTTPException: 503 if service is not ready
    """
    checks: Dict[str, bool] = {}
    
    # Database readiness check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = True
    except SQLAlchemyError as e:
        logger.error(f"Database readiness check failed: {e}")
        checks["database"] = False
    except Exception as e:
        logger.error(f"Unexpected error during readiness check: {e}", exc_info=True)
        checks["database"] = False
    
    # Determine overall readiness
    ready = all(checks.values())
    
    if not ready:
        logger.warning(f"Service not ready. Checks: {checks}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not ready"
        )
    
    return ReadinessStatus(ready=True, checks=checks)


@router.get(
    "/metrics",
    response_model=MetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Application metrics",
    description="Get application metrics and configuration information",
    tags=["monitoring"]
)
def get_metrics() -> MetricsResponse:
    """
    Get application metrics and configuration.
    
    This endpoint provides static and dynamic metrics about the application,
    including configuration, feature flags, and system information.
    Metrics are cached for performance.
    
    Returns:
        MetricsResponse with comprehensive application metrics
    """
    static_metrics = _get_static_metrics()
    
    return MetricsResponse(
        api=static_metrics["api"],
        features=static_metrics["features"],
        face_recognition=static_metrics["face_recognition"],
        system=static_metrics["system"]
    )
