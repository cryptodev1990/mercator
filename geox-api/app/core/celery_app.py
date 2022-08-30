"""Celery queue."""
from celery import Celery

from app.core.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "worker", broker=_settings.redis_connection, backend=_settings.redis_connection
)

celery_app.conf.task_routes = {
    "app.worker.test_celery": "main-queue",
    "app.worker.copy_to_s3": "main-queue",
}
