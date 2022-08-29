from fastapi import APIRouter, Depends, Request, Security

from app.core.celery_app import celery_app
from app.dependencies import UserSession, get_app_user_session, verify_token

from app.crud.organization import get_active_org


from app.schemas import CeleryTaskResponse, CeleryTaskResult
from app.worker import test_celery, copy_to_s3

from pydantic import UUID4

router = APIRouter(tags=["geofencer"], dependencies=[Depends(verify_token)])


@router.get(
    "/tasks/results/{task_id}",
    response_model=CeleryTaskResult,
    tags=["tasks"],
)
def get_status(task_id: str):
    """Retrieve results of a market selection task."""
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


@router.post("/tasks/copy_shapes", tags=["tasks"], response_model=CeleryTaskResponse)
def run_copy_task(
    user_session: UserSession = Depends(
        get_app_user_session),
):
    """Run a test celery task."""
    user = user_session.user
    org_id = get_active_org(user_session.session, user_session.user.id)

    task = copy_to_s3.delay(org_id)
    return CeleryTaskResponse(task_id=task.id)
