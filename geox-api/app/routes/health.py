from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_session, verify_token
from app.schemas.user import User

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    return {"message": "OK"}


@router.get("/protected_health", tags=["health"], dependencies=[Depends(verify_token)])
async def protected_health():
    return {"message": "OK"}


@router.get("/db-health", tags=["health"])
async def db_health(session: Session = Depends(get_session)):
    try:
        res = session.execute(text("SELECT 1")).scalar()
        assert res == 1
        return JSONResponse({"message": "OK"})
    except Exception as e:
        return JSONResponse({"message": "ERROR"}, status_code=500)
