import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.models import Task, Habit, Reminder, User
from app.services.pyswisseph_panchang import calculate_precise_panchang
from app.services.notifications.email_service import send_email

scheduler = BackgroundScheduler()

def check_upcoming_reminders():
    """Checks for reminders scheduled in the next 1 minute and fires alerts."""
    db = None
    try:
        db = SessionLocal()
        now = datetime.datetime.now(datetime.UTC)
        window = now + datetime.timedelta(minutes=5)
        
        reminders = db.query(Reminder).filter(
            Reminder.status == "Pending",
            Reminder.time >= now,
            Reminder.time <= window
        ).all()
        
        for r in reminders:
            # Fetch user email
            user = db.query(User).filter(User.id == r.user_id).first()
            if user:
                # Trigger Email notification
                subject = "LifeOS Reminder Alert"
                content = f"<h3>Reminder Alert</h3><p>Your task reminder is scheduled now: {r.time.isoformat()}</p>"
                success = send_email(user.email, subject, content)
                if success:
                    r.status = "Sent"
        db.commit()
    except Exception as e:
        print(f"[Scheduler Job Error] Reminders check failed: {e}")
    finally:
        if db:
            db.close()

def daily_panchang_digest():
    """Computes daily Panchang at Sunrise and alerts users of Ekadashi or festivals."""
    db = None
    try:
        db = SessionLocal()
        today = datetime.date.today()
        users = db.query(User).filter(User.is_active == True).all()
        
        # New Delhi coordinates default
        panchang = calculate_precise_panchang(today, 28.6139, 77.2090)
        
        if panchang["festivals"]:
            fest_list = ", ".join(panchang["festivals"])
            for u in users:
                send_email(
                    u.email,
                    f"LifeOS spiritual alerts - {today.isoformat()}",
                    f"<h3>Auspicious Alerts</h3><p>Today is: <strong>{panchang['tithi']}</strong></p>"
                    f"<p>Festivals observed today: <strong>{fest_list}</strong></p>"
                    f"<p>Auspicious Abhijit Muhurat: 11:45 AM - 12:35 PM</p>"
                )
    except Exception as e:
        print(f"[Scheduler Job Error] Panchang digest failed: {e}")
    finally:
        if db:
            db.close()

def initialize_scheduler():
    # Run task checks every 60 seconds
    scheduler.add_job(check_upcoming_reminders, 'interval', seconds=60, id='reminders_job')
    # Run daily digest at 6:00 AM local server time
    scheduler.add_job(daily_panchang_digest, 'cron', hour=6, minute=0, id='panchang_digest_job')
    scheduler.start()
    print("[Scheduler Service] APScheduler daemon initialized and running.")

def shutdown_scheduler():
    scheduler.shutdown()
    print("[Scheduler Service] APScheduler daemon stopped.")
