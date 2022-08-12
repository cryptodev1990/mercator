from fastapi import APIRouter, Depends, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import verify_token

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    return {"message": "OK"}


@router.get("/protected_health", tags=["health"], dependencies=[Depends(verify_token)])
async def protected_health():
    return {"message": "OK"}


@router.get("/db-health", tags=["health"])
async def db_health(db_session: Session = Depends(get_db)):
    try:
        res = db_session.execute("SELECT 1").scalar()
        assert res == 1
        return JSONResponse({"message": "OK"})
    except Exception as e:
        return JSONResponse({"message": "ERROR"}, status_code=500)
