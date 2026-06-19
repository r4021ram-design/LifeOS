import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.db import engine, Base, get_db
from app.core.config import settings
from app.api.v1 import auth, tasks, habits, goals, notes, trading, panchang, ai, health, search
from app.core.metrics import metrics_router

# Initialize Sentry only in staging and production
if settings.ENVIRONMENT in ["staging", "production"] and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0
    )

# Auto-create tables for SQLite / development/testing environments
if settings.ENVIRONMENT in ["development", "testing"]:
    Base.metadata.create_all(bind=engine)

from contextlib import asynccontextmanager
from app.services.notifications.scheduler import initialize_scheduler, shutdown_scheduler
from app.core.telemetry import initialize_telemetry

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize OTel and APScheduler
    initialize_telemetry(app, engine=engine)
    initialize_scheduler()
    yield
    # Shutdown: Stop APScheduler
    shutdown_scheduler()

app = FastAPI(
    title="LifeOS AI API",
    description="Institutional Grade Productivity & Reminder Platform Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Custom Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under v1 namespace
app.include_router(auth.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")
app.include_router(habits.router, prefix="/api/v1")
app.include_router(goals.router, prefix="/api/v1")
app.include_router(notes.router, prefix="/api/v1")
app.include_router(trading.router, prefix="/api/v1")
app.include_router(panchang.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(metrics_router)

# Top-level Health check aliases for container orchestrations
@app.get("/api/live")
def top_live():
    return health.liveness_check()

@app.get("/api/ready")
def top_ready(db = Depends(get_db)):
    return health.readiness_check(db)

@app.get("/api/health")
def top_health(db = Depends(get_db)):
    return health.deep_health_check(db)



@app.get("/")
def read_root():
    return {"message": "Welcome to LifeOS AI API Services"}
