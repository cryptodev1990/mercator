from asyncio.log import logger

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.tasks import run_market_selection
from app.model import MarketSelectionInput

router = APIRouter()

@router.post("/tasks/market_selection")
async def run_market_selection(input: MarketSelectionInput):
    task = run_market_selection()
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

