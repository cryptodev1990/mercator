import os

import redis
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..models.db import engine

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    return {"message": "OK"}


@router.get("/protected_health", tags=["health"])
async def protected_health():
    return {"message": "OK"}


@router.get("/redis-health", tags=["health"])
async def redis_health():
    r = redis.Redis.from_url(url=str(os.getenv("REDIS_CONNECTION")))
    try:
        res = r.ping()
        return JSONResponse({"message": "OK"})
    except redis.exceptions.ConnectionError:
        return JSONResponse({"message": "ERROR"}, status_code=500)


@router.get("/db-health", tags=["health"])
async def db_health():
    try:
        res = engine.execute("SELECT 1")
        assert res.first()[0] == 1
        return JSONResponse({"message": "OK"})
    except Exception as e:
        print(e)
        return JSONResponse({"message": "ERROR"}, status_code=500)
