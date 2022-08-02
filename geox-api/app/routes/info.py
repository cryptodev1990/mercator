from fastapi import APIRouter, Depends, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials

from app.core.config import Settings, get_settings
from app.schemas import AppVersion

router = APIRouter()


@router.get("/info", response_model=AppVersion)
async def info(settings: Settings = Depends(get_settings)):
    """Return app info."""
    return AppVersion(version=settings.version, git_commit=settings.git_commit)
