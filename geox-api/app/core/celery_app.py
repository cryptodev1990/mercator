"""Celery queue."""
from celery import Celery

from app.core.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "worker", broker=_settings.redis_connection, backend=_settings.redis_connection
)
