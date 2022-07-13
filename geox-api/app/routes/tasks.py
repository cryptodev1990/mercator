from typing import Any, Optional

from app.tasks import add, celery_app
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class CeleryTaskRunResponse(BaseModel):
    """Response from submitting a celery task."""

    task_id: str


class CeleryTaskResult(BaseModel):
    """Response from a celery task.

    This is currently agnostic to the type of task.
    """

    task_id: Any = Field(..., description="Task id")
    task_status: str = Field(..., description="Task status.")
    task_result: Any = Field(..., description="Task result value.")


@router.post("/tasks/add", tags=["tasks"], response_model=CeleryTaskRunResponse)
async def run_add_task(a: int, b: int):
    task = add.delay(a, b)
    return CeleryTaskRunResponse(task_id=task.id)


@router.get("/tasks/{task_id}", response_model=CeleryTaskResult, tags=["tasks"])
def get_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    return CeleryTaskResult(
        task_id=task_id, task_status=task_result.status, task_result=task_result.result
    )
