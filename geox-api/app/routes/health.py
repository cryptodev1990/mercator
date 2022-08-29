from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_db, verify_token, get_current_user
from app.schemas.user import User

router = APIRouter()


@router.get("/health", tags=["health"])
async def health():
    return {"message": "OK"}


@router.get("/protected_health", tags=["health"], dependencies=[Depends(verify_token)])
async def protected_health(user: User = Depends(get_current_user)):
    return {"message": "OK"}


@router.get("/db-health", tags=["health"])
async def db_health(db_session: Session = Depends(get_db)):
    try:
        res = db_session.execute(text("SELECT 1")).scalar()
        assert res == 1
        return JSONResponse({"message": "OK"})
    except Exception as e:
        return JSONResponse({"message": "ERROR"}, status_code=500)
