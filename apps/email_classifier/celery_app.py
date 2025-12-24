from celery import Celery
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "email_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["apps.email_classifier.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Madrid",
    enable_utc=True,
    broker_use_ssl={
        'ssl_cert_reqs': 'none'
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': 'none'
    }
)