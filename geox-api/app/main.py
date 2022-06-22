import json
import os

import redis

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.tasks import add, celery_app
from .model import GeoLiftParams

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"message": "OK"}


@app.get("/redis-health")
async def health():
    r = redis.Redis.from_url(url=os.getenv("REDIS_CONNECTION"))
    try:
        res = r.ping()
        print(res)
        return JSONResponse({"message": "OK"})
    except redis.exceptions.ConnectionError:
        return JSONResponse({"message": "ERROR"}, status_code=500)


@app.post("/geolift/validate")
async def validate_params(params: GeoLiftParams):
    return json.dumps(params)


@app.post("/tasks/add")
async def run_add_task(a: int, b: int):
    task = add.delay(a, b)
    return JSONResponse({"task_id": task.id})


@app.get("/tasks/{task_id}")
def get_status(task_id):
    task_result = celery_app.AsyncResult(task_id)
    print(task_result.backend)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return JSONResponse(result)
