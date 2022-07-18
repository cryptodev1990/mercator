from fastapi import APIRouter, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials

from app.db.session import engine
from .common import security

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    return {"message": "OK"}


@router.get("/protected_health", tags=["health"])
async def protected_health(
    credentials: HTTPAuthorizationCredentials = Security(security),
):
    return {"message": "OK"}


@router.get("/db-health", tags=["health"])
async def db_health():
    try:
        res = engine.execute("SELECT 1")
        assert res.first()[0] == 1
        return JSONResponse({"message": "OK"})
    except Exception as e:
        print(e)
        return JSONResponse({"message": "ERROR"}, status_code=500)
