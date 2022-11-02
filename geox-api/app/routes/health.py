"""Health routes."""
import ddtrace
from datadog import statsd
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from prometheus_client import Counter
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.dependencies import get_connection, verify_token

router = APIRouter()

# simple counter to ensure metrics are working properly
health_counter = Counter(
    "health_count", "Number of times the /health endpoint was called"
)


@router.get("/health", tags=["health"])
async def health():
    with ddtrace.tracer.trace("health_check"):
        health_counter.inc()
        statsd.increment("health_check")
        return {"message": "OK"}


@router.get("/protected_health", tags=["health"], dependencies=[Depends(verify_token)])
async def protected_health():
    return {"message": "OK"}


@router.get("/db-health", tags=["health"])
async def db_health(conn: Connection = Depends(get_connection)):
    try:
        res = conn.execute(text("SELECT 1")).scalar()
        assert res == 1
        return JSONResponse({"message": "OK"})
    except Exception as e:
        return JSONResponse({"message": "ERROR"}, status_code=500)
