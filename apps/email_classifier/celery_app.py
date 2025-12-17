from celery import Celery
from config import REDIS_URL

celery_app = Celery(
    "email_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["apps.email_classifier.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Madrid",
    enable_utc=True,
)