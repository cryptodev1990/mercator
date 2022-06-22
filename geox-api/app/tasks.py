import os

from random import random
import time

from celery import Celery

REDIS_CONNECTION = os.getenv("REDIS_CONNECTION", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks", broker=REDIS_CONNECTION, backend=REDIS_CONNECTION
)


@celery_app.task
def add(x: int, y: int):
    """Dummy task to add two numbers in a Celery worker"""
    time.sleep(random() * 5)
    return x + y
