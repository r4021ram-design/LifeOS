# LifeOS AI – Final Go-Live Release Checklist

This document acts as the official launch checklist for LifeOS AI. All tasks must be signed off by engineering and SRE leads before opening traffic to users.

## 1. Security & Compliance
- [x] **Strict CORS Policy:** Wildcard `*` origins removed. Only specified hostnames in `CORS_ALLOWED_ORIGINS` are accepted.
- [x] **SQL Injection Prevention:** SQLAlchemy ORM parameter binding utilized for all query paths; SQLite LIKE fallback used in local environments.
- [x] **Secure Headers:** X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, and HSTS headers added to all HTTP responses.
- [x] **Secrets Management:** Verification that no raw API credentials or tokens are committed to source control.

## 2. Code Quality & Performance
- [x] **FastAPI Lifespan:** Event startup/shutdown converted to async context manager.
- [x] **Python 3.14 Compatibility:** All instances of `datetime.utcnow()` removed in favor of `datetime.now(datetime.UTC)`.
- [x] **Pydantic v2 Migration:** Configuration classes refactored to `ConfigDict` and `SettingsConfigDict` to eliminate deprecation warnings.
- [x] **Test Coverage:** All 88 tests passing cleanly with zero warnings.

## 3. Database & Migrations
- [x] **DDL Gating:** Database table auto-generation disabled in production to prevent schema race conditions.
- [x] **Alembic Readiness:** Schema state managed entirely by versioned migrations.

## 4. Observability & Logging
- [x] **Sentry Monitoring:** Instrumented and configured to report errors from staging/production environments only.
- [x] **OpenTelemetry Integration:** Automatic instrumentation loaded for FastAPI, Redis, SQLAlchemy, and Celery during ASGI startup.
- [x] **Health Check Routing:** Separate `/api/live` and `/api/v1/health/ready` endpoints deployed.

## 5. Post-Deployment Smoke Test Actions
Once container deployment completes, verify:
1. Access `/api/v1/health/check` to confirm DB, Redis, and Celery connectivity are 100% healthy.
2. Sign up a new user, log in, create a mock reminder, and verify the Celery worker task processes the item.
3. Access the Prometheus metrics endpoint `/metrics` to ensure telemetry is exporting data correctly.
