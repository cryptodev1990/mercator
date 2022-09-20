from fastapi import APIRouter, Depends

from app.core.celery_app import celery_app
from app.core.config import Settings, get_settings
from app.dependencies import UserSession, get_app_user_session, verify_token
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


@router.post(
    "/tasks/copy_shapes",
    response_model=CeleryTaskResponse,
    deprecated=True,
    responses={
        403: {"description": "Data export not enabled for this account"},
        501: {"description": "Shape export is not configured"},
    },
)
def copy_shapes(
    user_session: UserSession = Depends(get_app_user_session),
    settings: Settings = Depends(get_settings)
) -> CeleryTaskResponse:
    """Export shapes to S3.

    This is an async task. Use `/tasks/results/{task_id}` to retieve the status and results.

    Exports all shapes in the user's organization to Snowflake, if the user's account is
    enabled for shape export, and the user has provided Snowflake account information for sharing.

    Use `POST /shapes/export` instead.

    """
    return run_shapes_export(user_session, settings)
