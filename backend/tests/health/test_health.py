import pytest
from unittest.mock import patch, MagicMock
from fastapi import status

def test_liveness_check(client):
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "live", "service": "LifeOS AI API"}

    response = client.get("/api/live")
    assert response.status_code == 200

@patch("app.api.v1.health.redis.from_url")
def test_readiness_check(mock_redis_url, client):
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    mock_redis_url.return_value = mock_redis

    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}

    response = client.get("/api/ready")
    assert response.status_code == 200

@patch("app.api.v1.health.redis.from_url")
def test_readiness_check_db_failure(mock_redis_url, client):
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    mock_redis_url.return_value = mock_redis

    # Force database check to fail
    with patch("sqlalchemy.orm.Session.execute", side_effect=Exception("DB connection error")):
        response = client.get("/api/v1/health/ready")
        assert response.status_code == 503
        assert "Database connection failed" in response.json()["detail"]

@patch("app.api.v1.health.redis.from_url")
def test_readiness_check_redis_failure(mock_redis_url, client):
    mock_redis_url.return_value.ping.side_effect = Exception("Redis offline")

    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert "Redis cache connection failed" in response.json()["detail"]

@patch("app.api.v1.health.redis.from_url")
@patch("app.core.celery_app.celery_app.control.ping")
def test_deep_health_check_healthy(mock_celery_ping, mock_redis_url, client):
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True
    mock_redis_url.return_value = mock_redis
    mock_celery_ping.return_value = [{"celery@worker": "pong"}]

    response = client.get("/api/v1/health/check")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["components"]["database"] == "healthy"
    assert data["components"]["redis"] == "healthy"
    assert data["components"]["celery"] == "healthy"

    response = client.get("/api/health")
    assert response.status_code == 200

@patch("app.api.v1.health.redis.from_url")
@patch("app.core.celery_app.celery_app.control.ping")
def test_deep_health_check_unhealthy(mock_celery_ping, mock_redis_url, client):
    # Test DB and Redis failure in check endpoint
    mock_redis = MagicMock()
    mock_redis.ping.side_effect = Exception("Redis error")
    mock_redis_url.return_value = mock_redis
    mock_celery_ping.return_value = []

    with patch("sqlalchemy.orm.Session.execute", side_effect=Exception("DB error")):
        response = client.get("/api/v1/health/check")
        assert response.status_code == 503
        data = response.json()["detail"]
        assert data["status"] == "unhealthy"
        assert "unhealthy" in data["components"]["database"]
        assert "unhealthy" in data["components"]["redis"]
        assert "unhealthy" in data["components"]["celery"]

@patch("app.api.v1.health.redis.from_url")
@patch("app.core.celery_app.celery_app.control.ping")
def test_deep_health_check_celery_exception(mock_celery_ping, mock_redis_url, client):
    mock_redis = MagicMock()
    mock_redis_url.return_value = mock_redis
    mock_celery_ping.side_effect = Exception("Celery broker connection failed")

    response = client.get("/api/v1/health/check")
    assert response.status_code == 503
    data = response.json()["detail"]
    assert "unhealthy: Celery broker connection failed" in data["components"]["celery"]

@patch("app.api.v1.health.redis.from_url")
@patch("app.core.celery_app.celery_app.control.ping")
def test_deep_health_check_ai_provider_variations(mock_celery_ping, mock_redis_url, client):
    mock_redis = MagicMock()
    mock_redis_url.return_value = mock_redis
    mock_celery_ping.return_value = [{"worker": "pong"}]

    # Case 1: OpenAI and Gemini both present
    with patch("app.api.v1.health.settings") as mock_settings:
        mock_settings.REDIS_URL = "redis://localhost:6379"
        mock_settings.OPENAI_API_KEY = "sk-openai"
        mock_settings.GEMINI_API_KEY = "ai-gemini"
        
        response = client.get("/api/v1/health/check")
        assert response.status_code == 200
        assert response.json()["components"]["ai_providers"] == ["OpenAI", "Gemini"]

    # Case 2: OpenAI present, Gemini absent
    with patch("app.api.v1.health.settings") as mock_settings:
        mock_settings.REDIS_URL = "redis://localhost:6379"
        mock_settings.OPENAI_API_KEY = "sk-openai"
        mock_settings.GEMINI_API_KEY = ""
        
        response = client.get("/api/v1/health/check")
        assert response.status_code == 200
        assert response.json()["components"]["ai_providers"] == ["OpenAI"]

    # Case 3: Neither present (mock simulation)
    with patch("app.api.v1.health.settings") as mock_settings:
        mock_settings.REDIS_URL = "redis://localhost:6379"
        mock_settings.OPENAI_API_KEY = ""
        mock_settings.GEMINI_API_KEY = ""
        
        response = client.get("/api/v1/health/check")
        assert response.status_code == 200
        assert response.json()["components"]["ai_providers"] == "mock (No keys loaded)"
