from http.client import HTTPException

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from app.core.celery_app import celery_app
from app.crud.organization import get_active_org, organization_s3_enabled
from app.dependencies import UserSession, get_app_user_session, verify_token
from app.schemas import CeleryTaskResponse, CeleryTaskResult
from app.worker import copy_to_s3, test_celery

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


@router.post("/tasks/test", tags=["tasks"], response_model=CeleryTaskResponse)
def run_test_celery(word: str = "Hello"):
    """Run a test celery task."""
    task = test_celery.delay(word)
    return CeleryTaskResponse(task_id=task.id)

@router.post("/tasks/copy_shapes", response_model=CeleryTaskResponse, deprecated=True,
             responses = {403: {"description": "Data export not enabled for this account"}})
def shapes_export(
    user_session: UserSession = Depends(get_app_user_session),
):
    """Export shapes to S3.

    This is an async task. Use `/tasks/results/{task_id}` to retieve the status and results.

    Use `POST /shapes/export` instead.

    """
    org_id = get_active_org(user_session.session, user_session.user.id)
    # TODO: this should be a permission on shapes
    if not organization_s3_enabled(user_session.session, str(org_id)):
        raise HTTPException(
            status_code=403, detail="Data export is not enabled for this account."  # type: ignore
        )
    task = copy_to_s3.delay(org_id)
    return CeleryTaskResponse(task_id=task.id)
