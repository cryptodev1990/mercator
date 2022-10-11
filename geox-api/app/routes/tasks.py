from fastapi import APIRouter, Depends

from app.core.celery_app import celery_app
from app.core.config import Settings, get_settings
from app.dependencies import UserConnection, get_app_user_connection, verify_token
from app.routes.shapes import run_shapes_export
from app.schemas import CeleryTaskResponse, CeleryTaskResult
from app.worker import test_celery

router = APIRouter(tags=["geofencer"], dependencies=[Depends(verify_token)])


@router.get(
    "/tasks/results/{task_id}",
    response_model=CeleryTaskResult,
    tags=["tasks"],
)
def get_status(task_id: str):
    """Retrieve results of a task."""
    task_result = celery_app.AsyncResult(task_id)
    result = CeleryTaskResult(
        task_id=task_id, task_status=task_result.status, task_result=task_result.result
    )
    return result


@router.post(
    "/tasks/test",
    tags=["tasks"],
    response_model=CeleryTaskResponse,
)
def run_test_celery(word: str = "Hello"):
    """Run a test celery task."""
    task = test_celery.delay(word)
    return CeleryTaskResponse(task_id=task.id)
