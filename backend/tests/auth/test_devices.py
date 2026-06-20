import pytest
from app.models.models import DeviceToken

def test_register_device_success(client, auth_headers, test_user):
    payload = {
        "token": "fcm_test_token_12345",
        "platform": "android",
        "device_name": "Test Android Phone"
    }
    response = client.post("/api/v1/devices/register", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["token"] == "fcm_test_token_12345"
    assert data["platform"] == "android"
    assert data["device_name"] == "Test Android Phone"
    assert data["user_id"] == test_user.id
    assert "id" in data

def test_register_device_rotation(client, auth_headers, test_user, db):
    # Register once
    payload = {
        "token": "fcm_test_token_rotation",
        "platform": "android",
        "device_name": "Device Original"
    }
    response = client.post("/api/v1/devices/register", json=payload, headers=auth_headers)
    assert response.status_code == 200
    original_id = response.json()["id"]

    # Register again with same token but new parameters
    payload_update = {
        "token": "fcm_test_token_rotation",
        "platform": "ios",
        "device_name": "Device Rotated"
    }
    response = client.post("/api/v1/devices/register", json=payload_update, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == original_id
    assert data["platform"] == "ios"
    assert data["device_name"] == "Device Rotated"

    # Confirm there is only 1 device in database with this token
    count = db.query(DeviceToken).filter(DeviceToken.token == "fcm_test_token_rotation").count()
    assert count == 1

def test_register_device_unauthorized(client):
    payload = {
        "token": "fcm_test_token_no_auth",
        "platform": "android"
    }
    response = client.post("/api/v1/devices/register", json=payload)
    assert response.status_code == 401
