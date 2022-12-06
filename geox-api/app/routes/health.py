"""Health routes."""
from typing import Dict

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.dependencies import get_connection, verify_subscription, verify_token

import time

router = APIRouter()


@router.get("/health", tags=["health"])
async def health() -> Dict[str, str]:
    return {"message": "OK"}


@router.get("/health_time", tags=["health"])
async def time_health() -> Dict[str, str]:
    """Delays for 0.1 seconds to simulate a slow response. Used for debugging the ASGI server."""
    time.sleep(0.1)
    return {"message": "OK"}


@router.get("/protected_health", tags=["health"], dependencies=[Depends(verify_token)])
async def protected_health() -> Dict[str, str]:
    return {"message": "OK"}


@router.get(
    "/subscription_health",
    tags=["health"],
    dependencies=[Depends(verify_token), Depends(verify_subscription)],
)
async def subscription_health() -> Dict[str, str]:
    return {"message": "OK"}


@router.get("/db_health", tags=["health"])
async def db_health(conn: Connection = Depends(get_connection)) -> JSONResponse:
    try:
        res = conn.execute(text("SELECT 1")).scalar()
        assert res == 1
        return JSONResponse({"message": "OK"})
    except Exception:  # pylint: disable=broad-except
        return JSONResponse({"message": "ERROR"}, status_code=500)
