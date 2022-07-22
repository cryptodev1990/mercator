"""Celery worker."""
from app.core.celery_app import celery_app


@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    """Dummy task to return a work in a Celery worker."""
    return f"test task return {word}"
