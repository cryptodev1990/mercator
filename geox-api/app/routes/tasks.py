
from fastapi import APIRouter, Request, Security
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4

from app.crud import shape as crud
from app.db.session import SessionLocal
from app.schemas import (
    CeleryTaskResult,
    CeleryTaskResponse
)
from app.core.celery_app import celery_app
from app.worker import test_celery

router = APIRouter()


@router.get(
    "/tasks/results/{task_id}",
    response_model=CeleryTaskResult,
    tags=["tasks"],
)
def get_status(task_id: str):
    """Retrieve results of a market selection task."""
    task_result = celery_app.AsyncResult(task_id)
    result = CeleryTaskResult(task_id=task_id, task_status=task_result.status, task_result=task_result.result)
    return result


@router.post("/tasks/test", tags=["tasks"], response_model=CeleryTaskResponse)
async def run_test_celery(word: str = "Hello"):
    """Run a test celery task."""
    task = test_celery.delay(word)
    return CeleryTaskResponse(task_id=task.id)
