import asyncio
from app.core.celery_app import celery_app
from app.core.db import SessionLocal
from app.models.models import Notification, NotificationAttempt
from app.services.notifications.email_service import send_email
from app.services.notifications.push_service import send_push_notification

@celery_app.task(bind=True, max_retries=3, name="send_async_email_task")
def send_async_email_task(self, to_email: str, subject: str, html_content: str, user_id: int, notification_id: int = None):
    """
    Asynchronously transmits email notifications with exponential backoff retries.
    Audits each delivery attempt in the database.
    """
    db = SessionLocal()
    try:
        # Create an attempt record
        attempt = NotificationAttempt(
            notification_id=notification_id,
            attempt_number=self.request.retries + 1,
            status="Pending"
        )
        if notification_id:
            db.add(attempt)
            db.commit()

        success = send_email(to_email, subject, html_content)
        if success:
            attempt.status = "Sent"
            if notification_id:
                notif = db.query(Notification).filter(Notification.id == notification_id).first()
                if notif:
                    notif.status = "Sent"
                    notif.retry_count = self.request.retries
            db.commit()
            return True
        else:
            raise RuntimeError("SMTP provider failed to send email.")

    except Exception as e:
        db.rollback()
        attempt.status = "Failed"
        attempt.error_message = str(e)
        if notification_id:
            notif = db.query(Notification).filter(Notification.id == notification_id).first()
            if notif:
                notif.retry_count = self.request.retries + 1
                notif.last_error = str(e)
                if self.request.retries >= self.max_retries:
                    notif.status = "Failed"  # Moved to DLQ/Failed state
            db.add(attempt)
            db.commit()

        # Exponential backoff retry: (2^retries) * 60 seconds
        countdown = (2 ** self.request.retries) * 60
        raise self.retry(exc=e, countdown=countdown)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, name="send_async_push_task")
def send_async_push_task(self, user_token: str, title: str, body: str, user_id: int, notification_id: int = None):
    """
    Asynchronously transmits mobile push notifications with exponential backoff retries.
    Audits each delivery attempt in the database.
    """
    db = SessionLocal()
    try:
        # Create an attempt record
        attempt = NotificationAttempt(
            notification_id=notification_id,
            attempt_number=self.request.retries + 1,
            status="Pending"
        )
        if notification_id:
            db.add(attempt)
            db.commit()

        # Run async function in Celery sync context
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Run in a separate thread/executor to avoid blocking the event loop
            future = asyncio.run_coroutine_threadsafe(send_push_notification(user_token, title, body), loop)
            success = future.result()
        else:
            success = loop.run_until_complete(send_push_notification(user_token, title, body))

        if success:
            attempt.status = "Sent"
            if notification_id:
                notif = db.query(Notification).filter(Notification.id == notification_id).first()
                if notif:
                    notif.status = "Sent"
                    notif.retry_count = self.request.retries
            db.commit()
            return True
        else:
            raise RuntimeError("FCM push delivery failed.")

    except Exception as e:
        db.rollback()
        attempt.status = "Failed"
        attempt.error_message = str(e)
        if notification_id:
            notif = db.query(Notification).filter(Notification.id == notification_id).first()
            if notif:
                notif.retry_count = self.request.retries + 1
                notif.last_error = str(e)
                if self.request.retries >= self.max_retries:
                    notif.status = "Failed"
            db.add(attempt)
            db.commit()

        # Exponential backoff retry: (2^retries) * 60 seconds
        countdown = (2 ** self.request.retries) * 60
        raise self.retry(exc=e, countdown=countdown)
    finally:
        db.close()
