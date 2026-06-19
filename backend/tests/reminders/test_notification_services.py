import pytest
import smtplib
import socket
from unittest.mock import patch, MagicMock
import httpx
from app.services.notifications.email_service import send_email
from app.services.notifications.push_service import send_push_notification

# ================= EMAIL SERVICE TESTS =================

@patch("app.services.notifications.email_service.SMTP_USER", "user@test.com")
@patch("app.services.notifications.email_service.SMTP_PASSWORD", "password123")
@patch("app.services.notifications.email_service.smtplib.SMTP")
def test_send_email_success(mock_smtp_class):
    mock_server = MagicMock()
    mock_smtp_class.return_value.__enter__.return_value = mock_server
    
    res = send_email("recipient@test.com", "Test Subject", "<p>Hello</p>")
    
    assert res is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with("user@test.com", "password123")
    mock_server.sendmail.assert_called_once()

@patch("app.services.notifications.email_service.SMTP_USER", "")
@patch("app.services.notifications.email_service.SMTP_PASSWORD", "")
def test_send_email_development_fallback():
    # When keys are missing, it logs to output and returns True
    res = send_email("recipient@test.com", "Test Subject", "<p>Hello</p>")
    assert res is True

@patch("app.services.notifications.email_service.SMTP_USER", "user@test.com")
@patch("app.services.notifications.email_service.SMTP_PASSWORD", "password123")
@patch("app.services.notifications.email_service.smtplib.SMTP")
def test_send_email_timeout(mock_smtp_class):
    mock_server = MagicMock()
    mock_server.starttls.side_effect = socket.timeout("Connection timed out")
    mock_smtp_class.return_value.__enter__.return_value = mock_server

    res = send_email("recipient@test.com", "Test Subject", "<p>Hello</p>")
    assert res is False

@patch("app.services.notifications.email_service.SMTP_USER", "user@test.com")
@patch("app.services.notifications.email_service.SMTP_PASSWORD", "password123")
@patch("app.services.notifications.email_service.smtplib.SMTP")
def test_send_email_auth_failure(mock_smtp_class):
    mock_server = MagicMock()
    mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
    mock_smtp_class.return_value.__enter__.return_value = mock_server

    res = send_email("recipient@test.com", "Test Subject", "<p>Hello</p>")
    assert res is False

@patch("app.services.notifications.email_service.SMTP_USER", "user@test.com")
@patch("app.services.notifications.email_service.SMTP_PASSWORD", "password123")
@patch("app.services.notifications.email_service.smtplib.SMTP")
def test_send_email_connection_reset(mock_smtp_class):
    mock_server = MagicMock()
    mock_server.sendmail.side_effect = smtplib.SMTPServerDisconnected("Connection closed by remote host")
    mock_smtp_class.return_value.__enter__.return_value = mock_server

    res = send_email("recipient@test.com", "Test Subject", "<p>Hello</p>")
    assert res is False

@patch("app.services.notifications.email_service.SMTP_USER", "user@test.com")
@patch("app.services.notifications.email_service.SMTP_PASSWORD", "password123")
@patch("app.services.notifications.email_service.smtplib.SMTP")
def test_send_email_generic_smtp_exception(mock_smtp_class):
    mock_server = MagicMock()
    mock_smtp_class.side_effect = smtplib.SMTPException("SMTP protocol error")

    res = send_email("recipient@test.com", "Test Subject", "<p>Hello</p>")
    assert res is False


# ================= PUSH NOTIFICATION TESTS =================

@patch("app.services.notifications.push_service.FCM_SERVER_KEY", "")
@pytest.mark.anyio
async def test_send_push_fallback_missing_key():
    # Returns True when FCM key is missing (local simulator)
    res = await send_push_notification("dev-token", "Hello", "World")
    assert res is True

@patch("app.services.notifications.push_service.FCM_SERVER_KEY", "")
@pytest.mark.anyio
async def test_send_push_fallback_missing_token():
    # Returns True when device token is empty
    res = await send_push_notification("", "Hello", "World")
    assert res is True

@patch("app.services.notifications.push_service.FCM_SERVER_KEY", "fcm_key_123")
@patch("app.services.notifications.push_service.httpx.AsyncClient.post")
@pytest.mark.anyio
async def test_send_push_success(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp

    res = await send_push_notification("device-token-abc", "LifeOS Notification", "Test body")
    assert res is True
    
    # Assert headers and format
    args, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "key=fcm_key_123"
    assert kwargs["json"]["to"] == "device-token-abc"

@patch("app.services.notifications.push_service.FCM_SERVER_KEY", "fcm_key_123")
@patch("app.services.notifications.push_service.httpx.AsyncClient.post")
@pytest.mark.anyio
async def test_send_push_invalid_device_token(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_post.return_value = mock_resp

    res = await send_push_notification("bad-device-token", "Title", "Body")
    assert res is False

@patch("app.services.notifications.push_service.FCM_SERVER_KEY", "fcm_key_123")
@patch("app.services.notifications.push_service.httpx.AsyncClient.post")
@pytest.mark.anyio
async def test_send_push_rate_limit(mock_post):
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_post.return_value = mock_resp

    res = await send_push_notification("device-token", "Title", "Body")
    assert res is False

@patch("app.services.notifications.push_service.FCM_SERVER_KEY", "fcm_key_123")
@patch("app.services.notifications.push_service.httpx.AsyncClient.post")
@pytest.mark.anyio
async def test_send_push_timeout(mock_post):
    mock_post.side_effect = httpx.TimeoutException("FCM request timed out")

    res = await send_push_notification("device-token", "Title", "Body")
    assert res is False

@patch("app.services.notifications.push_service.FCM_SERVER_KEY", "fcm_key_123")
@patch("app.services.notifications.push_service.httpx.AsyncClient.post")
@pytest.mark.anyio
async def test_send_push_connect_error(mock_post):
    mock_post.side_effect = httpx.ConnectError("Could not resolve FCM server host")

    res = await send_push_notification("device-token", "Title", "Body")
    assert res is False
