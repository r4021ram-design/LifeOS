import datetime
import asyncio
from unittest.mock import patch, MagicMock
import pytest
from app.models.models import Reminder, Notification, NotificationAttempt, User
from app.services.notifications.scheduler import check_upcoming_reminders, daily_panchang_digest, initialize_scheduler, shutdown_scheduler
from app.services.notifications.worker import send_async_email_task, send_async_push_task
from celery.app.task import Context

def test_check_upcoming_reminders_triggers_email(db, test_user):
    # Setup reminder in the 5-minute window
    now = datetime.datetime.now(datetime.UTC)
    reminder = Reminder(
        user_id=test_user.id,
        type="One Time",
        time=now + datetime.timedelta(minutes=2),
        status="Pending",
        timing_offset_minutes=0
    )
    db.add(reminder)
    db.commit()

    # Prevent db.close() from detaching our objects in tests
    db.close = MagicMock()

    # Mock SessionLocal and SMTP email send to succeed
    with patch("app.services.notifications.scheduler.SessionLocal", return_value=db):
        with patch("app.services.notifications.scheduler.send_email", return_value=True) as mock_send:
            check_upcoming_reminders()
            mock_send.assert_called_once()
            
            # Verify status updated to Sent
            db.refresh(reminder)
            assert reminder.status == "Sent"

def test_check_upcoming_reminders_exception_handling():
    # Verify exception is caught and logged
    with patch("app.services.notifications.scheduler.SessionLocal", side_effect=Exception("Database error")):
        with patch("builtins.print") as mock_print:
            check_upcoming_reminders()
            mock_print.assert_any_call("[Scheduler Job Error] Reminders check failed: Database error")

def test_daily_panchang_digest_success(db, test_user):
    db.close = MagicMock()
    # Mock calculate_precise_panchang and send_email
    with patch("app.services.notifications.scheduler.SessionLocal", return_value=db):
        with patch("app.services.notifications.scheduler.calculate_precise_panchang") as mock_panchang:
            mock_panchang.return_value = {
                "tithi": "Purnima",
                "festivals": ["Purnima Vrat"],
                "muhurats": ["Abhijit Muhurat"]
            }
            with patch("app.services.notifications.scheduler.send_email", return_value=True) as mock_send:
                daily_panchang_digest()
                mock_send.assert_called_once_with(
                    test_user.email,
                    f"LifeOS spiritual alerts - {datetime.date.today().isoformat()}",
                    f"<h3>Auspicious Alerts</h3><p>Today is: <strong>Purnima</strong></p>"
                    f"<p>Festivals observed today: <strong>Purnima Vrat</strong></p>"
                    f"<p>Auspicious Abhijit Muhurat: 11:45 AM - 12:35 PM</p>"
                )

def test_daily_panchang_digest_exception_handling():
    with patch("app.services.notifications.scheduler.SessionLocal", side_effect=Exception("DB Error")):
        with patch("builtins.print") as mock_print:
            daily_panchang_digest()
            mock_print.assert_any_call("[Scheduler Job Error] Panchang digest failed: DB Error")

def test_scheduler_lifecycle():
    with patch("app.services.notifications.scheduler.scheduler.start") as mock_start:
        with patch("app.services.notifications.scheduler.scheduler.add_job") as mock_add:
            initialize_scheduler()
            assert mock_start.call_count == 1
            assert mock_add.call_count == 2
            
    with patch("app.services.notifications.scheduler.scheduler.shutdown") as mock_shutdown:
        shutdown_scheduler()
        assert mock_shutdown.call_count == 1

@patch("app.services.notifications.worker.send_email")
def test_send_email_task_success(mock_send_email, db, test_user):
    mock_send_email.return_value = True
    
    # Create notification record
    notif = Notification(
        user_id=test_user.id,
        channel="Email",
        content="Welcome to LifeOS!",
        status="Pending"
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    db.close = MagicMock()

    with patch("app.services.notifications.worker.SessionLocal", return_value=db):
        res = send_async_email_task.run(
            to_email=test_user.email,
            subject="Welcome",
            html_content="<p>Welcome</p>",
            user_id=test_user.id,
            notification_id=notif.id
        )
        assert res is True
    
    attempts = db.query(NotificationAttempt).filter(NotificationAttempt.notification_id == notif.id).all()
    assert len(attempts) == 1
    assert attempts[0].status == "Sent"
    
    db.refresh(notif)
    assert notif.status == "Sent"

@patch("app.services.notifications.worker.send_email")
def test_send_email_task_failure_retry_and_dlq(mock_send_email, db, test_user):
    mock_send_email.return_value = False
    
    notif = Notification(
        user_id=test_user.id,
        channel="Email",
        content="Alert!",
        status="Pending"
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    db.close = MagicMock()

    context = Context(retries=3)
    send_async_email_task.request_stack.push(context)
    send_async_email_task.max_retries = 3

    try:
        with patch.object(send_async_email_task, "retry", side_effect=Exception("Retrying task")):
            with patch("app.services.notifications.worker.SessionLocal", return_value=db):
                with pytest.raises(Exception, match="Retrying task"):
                    send_async_email_task.run(
                        to_email=test_user.email,
                        subject="Alert",
                        html_content="<p>Alert</p>",
                        user_id=test_user.id,
                        notification_id=notif.id
                    )
    finally:
        send_async_email_task.request_stack.pop()

    db.refresh(notif)
    assert notif.status == "Failed"
    
    attempts = db.query(NotificationAttempt).filter(NotificationAttempt.notification_id == notif.id).all()
    assert len(attempts) == 1
    assert attempts[0].status == "Failed"
    assert "SMTP provider failed to send email." in attempts[0].error_message

@patch("app.services.notifications.worker.send_push_notification")
def test_send_push_task_success(mock_send_push, db, test_user):
    mock_send_push.return_value = True
    
    notif = Notification(
        user_id=test_user.id,
        channel="Push",
        content="Device message",
        status="Pending"
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    db.close = MagicMock()

    with patch("app.services.notifications.worker.SessionLocal", return_value=db):
        res = send_async_push_task.run(
            user_token="device-token-123",
            title="Push Title",
            body="Push Body",
            user_id=test_user.id,
            notification_id=notif.id
        )
        assert res is True

    attempts = db.query(NotificationAttempt).filter(NotificationAttempt.notification_id == notif.id).all()
    assert len(attempts) == 1
    assert attempts[0].status == "Sent"
    
    db.refresh(notif)
    assert notif.status == "Sent"

@patch("app.services.notifications.worker.send_push_notification")
def test_send_push_task_running_event_loop(mock_send_push, db, test_user):
    mock_send_push.return_value = True
    
    notif = Notification(
        user_id=test_user.id,
        channel="Push",
        content="Device message loop",
        status="Pending"
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    db.close = MagicMock()

    mock_loop = MagicMock()
    mock_loop.is_running.return_value = True
    mock_future = MagicMock()
    mock_future.result.return_value = True
    
    def dummy_run_coroutine_threadsafe(coro, loop):
        coro.close()
        return mock_future

    with patch("app.services.notifications.worker.SessionLocal", return_value=db):
        with patch("asyncio.get_event_loop", return_value=mock_loop):
            with patch("asyncio.run_coroutine_threadsafe", side_effect=dummy_run_coroutine_threadsafe) as mock_threadsafe:
                res = send_async_push_task.run(
                    user_token="device-token-123",
                    title="Push Title",
                    body="Push Body",
                    user_id=test_user.id,
                    notification_id=notif.id
                )
                assert res is True
                mock_threadsafe.assert_called_once()

@patch("app.services.notifications.worker.send_push_notification")
def test_send_push_task_failure_retry_and_dlq(mock_send_push, db, test_user):
    mock_send_push.return_value = False
    
    notif = Notification(
        user_id=test_user.id,
        channel="Push",
        content="Alert Push!",
        status="Pending"
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    db.close = MagicMock()

    context = Context(retries=3)
    send_async_push_task.request_stack.push(context)
    send_async_push_task.max_retries = 3

    try:
        with patch.object(send_async_push_task, "retry", side_effect=Exception("Retrying push task")):
            with patch("app.services.notifications.worker.SessionLocal", return_value=db):
                with pytest.raises(Exception, match="Retrying push task"):
                    send_async_push_task.run(
                        user_token="device-token-123",
                        title="Alert Title",
                        body="Alert Body",
                        user_id=test_user.id,
                        notification_id=notif.id
                    )
    finally:
        send_async_push_task.request_stack.pop()

    db.refresh(notif)
    assert notif.status == "Failed"
    
    attempts = db.query(NotificationAttempt).filter(NotificationAttempt.notification_id == notif.id).all()
    assert len(attempts) == 1
    assert attempts[0].status == "Failed"
    assert "FCM push delivery failed." in attempts[0].error_message
