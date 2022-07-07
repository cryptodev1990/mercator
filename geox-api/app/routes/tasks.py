from typing import Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.tasks import celery_app, run_market_selection_task, MarketSelectionResult, add
from app.model import MarketSelectionInput

router = APIRouter()


class CeleryTaskRunResponse(BaseModel):
    """Response from submitting a celery task."""

    task_id: str


class MarketSelectionTaskResult(BaseModel):
    task_id: Any = Field(..., description="Task id")
    task_status: str = Field(..., description="Task status.")
    task_result: Optional[MarketSelectionResult] = Field(
        ..., description="Market selection results."
    )


@router.post(
    "/tasks/market_selection", response_model=CeleryTaskRunResponse, tags=["geox"]
)
async def run_market_selection(input: MarketSelectionInput):
    """Submit a market selection task."""
    task = run_market_selection_task()
    return CeleryTaskRunResponse(task_id=task.id)


@router.get(
    "/tasks/market_selection/{task_id}",
    response_model=MarketSelectionTaskResult,
    tags=["geox"],
)
def get_status(task_id: str):
    """Retrieve results of a market selection task."""
    task_result = celery_app.AsyncResult(task_id)
    result = MarketSelectionTaskResult(
        task_id=task_id, task_status=task_result.status, task_result=task_result.result
    )
    return result


@router.post("/tasks/add", tags=["tasks"], response_model=CeleryTaskRunResponse)
async def run_add_task(a: int, b: int):
    task = add.delay(a, b)
    return CeleryTaskRunResponse(task_id=task.id)


class CeleryAddTaskResult(BaseModel):
    task_id: Any = Field(..., description="Task id")
    task_status: str = Field(..., description="Task status.")
    task_result: Optional[int] = Field(..., description="Sum")


@router.get("/tasks/{task_id}", response_model=CeleryAddTaskResult, tags=["tasks"])
def get_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    return CeleryAddTaskResult(
        task_id=task_id, task_status=task_result.status, task_result=task_result.result
    )
