from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis
from app.core.db import get_db
from app.core.config import settings
from app.services.pyswisseph_panchang import SWISSEPH_AVAILABLE

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/live", status_code=status.HTTP_200_OK)
def liveness_check():
    """Liveness check to verify the process is running."""
    return {"status": "live", "service": "LifeOS AI API"}

@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)):
    """Readiness check verifying database and Redis connections."""
    # Test DB
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {e}"
        )
    
    # Test Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Redis cache connection failed: {e}"
        )
        
    return {"status": "ready"}

@router.get("/check", status_code=status.HTTP_200_OK)
def deep_health_check(db: Session = Depends(get_db)):
    """Deep status checks mapping external systems configuration."""
    health_status = {
        "status": "healthy",
        "components": {}
    }
    
    # DB Check
    try:
        db.execute(text("SELECT 1"))
        health_status["components"]["database"] = "healthy"
    except Exception as e:
        health_status["components"]["database"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"

    # Redis Check
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["components"]["redis"] = "healthy"
    except Exception as e:
        health_status["components"]["redis"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"

    # Celery Worker Check
    try:
        from app.core.celery_app import celery_app
        ping_res = celery_app.control.ping(timeout=0.5)
        if ping_res:
            health_status["components"]["celery"] = "healthy"
        else:
            health_status["components"]["celery"] = "unhealthy (no workers responding)"
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["components"]["celery"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"

    # Panchang Engine Status
    health_status["components"]["panchang_engine"] = "precise (PySwissEph)" if SWISSEPH_AVAILABLE else "fallback (DateMath)"

    # AI Configuration Status
    ai_status = []
    if settings.OPENAI_API_KEY:
        ai_status.append("OpenAI")
    if settings.GEMINI_API_KEY:
        ai_status.append("Gemini")
    
    health_status["components"]["ai_providers"] = ai_status if ai_status else "mock (No keys loaded)"
    
    if health_status["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=health_status
        )
        
    return health_status
