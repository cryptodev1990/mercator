from ..tasks import add, celery_app

from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()


@router.post("/tasks/add")
async def run_add_task(a: int, b: int):
    task = add.delay(a, b)
    return JSONResponse({"task_id": task.id})


@router.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = celery_app.AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return JSONResponse(result)

