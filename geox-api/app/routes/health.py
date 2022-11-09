"""Health routes."""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from prometheus_client import Counter
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.stats import stats
from app.dependencies import get_connection, verify_subscription, verify_token

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    return {"message": "OK"}


@router.get("/protected_health", tags=["health"], dependencies=[Depends(verify_token)])
async def protected_health():
    return {"message": "OK"}


@router.get(
    "/subscription_health",
    tags=["health"],
    dependencies=[Depends(verify_token), Depends(verify_subscription)],
)
async def subscription_health():
    return {"message": "OK"}


@router.get("/db_health", tags=["health"])
async def db_health(conn: Connection = Depends(get_connection)):
    try:
        res = conn.execute(text("SELECT 1")).scalar()
        assert res == 1
        return JSONResponse({"message": "OK"})
    except Exception:  # pylint: disable=broad-except
        return JSONResponse({"message": "ERROR"}, status_code=500)
