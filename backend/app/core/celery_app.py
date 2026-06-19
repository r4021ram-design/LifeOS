from celery import Celery
from app.core.config import settings

REDIS_URL = settings.REDIS_URL

celery_app = Celery(
    "lifeos",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.services.notifications.worker"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
)
