import os
import json
import httpx

FCM_SERVER_KEY = os.getenv("FCM_SERVER_KEY", "")

async def send_push_notification(user_token: str, title: str, body: str) -> bool:
    """Sends Push Notification via FCM or simulates output for testing."""
    if not FCM_SERVER_KEY or not user_token:
        # Development fallback simulation
        print(f"[Push Notification Simulation] Token: {user_token[:15]}... | Title: {title} | Body: {body}")
        return True

    headers = {
        "Authorization": f"key={FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": user_token,
        "notification": {
            "title": title,
            "body": body,
            "sound": "default"
        }
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://fcm.googleapis.com/fcm/send",
                headers=headers,
                json=payload,
                timeout=10.0
            )
            return response.status_code == 200
    except Exception as e:
        print(f"[Push Notification Error] Failed to transmit: {e}")
        return False
