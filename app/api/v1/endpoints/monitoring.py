from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
import time

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": time.time()
    }

    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@router.get("/metrics")
def get_metrics() -> dict:
    """
    Get application metrics and configuration information.
    
    Returns:
        Dictionary containing API version, feature flags, and face recognition settings
    """
    return {
        "api_version": settings.VERSION,
        "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
        "compression_enabled": settings.ENABLE_COMPRESSION,
        "face_recognition_model": f"InsightFace {settings.INSIGHTFACE_MODEL}",
        "face_recognition_tolerance": settings.FACE_RECOGNITION_TOLERANCE,
        "embedding_dimensions": settings.EMBEDDING_DIMENSIONS
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")
