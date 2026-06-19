import pytest
from app.models.models import User
from app.core.security import create_refresh_token

def test_signup_success(client):
    payload = {
        "email": "new_user@lifeos.com",
        "password": "strongpassword123",
        "full_name": "New User"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new_user@lifeos.com"
    assert data["full_name"] == "New User"
    assert "id" in data

def test_signup_duplicate_email(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "somepassword123",
        "full_name": "Duplicate User"
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "The user with this email already exists in the system."

def test_login_success(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "testpassword"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_password(client, test_user):
    payload = {
        "email": test_user.email,
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

def test_refresh_token_success(client, test_user):
    refresh_token = create_refresh_token(subject=test_user.id)
    response = client.post(f"/api/v1/auth/refresh?refresh_token={refresh_token}")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_refresh_token_invalid(client):
    response = client.post("/api/v1/auth/refresh?refresh_token=invalidtoken123")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token"

def test_get_me(client, auth_headers, test_user):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
