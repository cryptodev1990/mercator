from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.db.app_user import get_app_user_id
from app.dependencies import UserConnection, get_app_user_connection
from app.schemas import AppVersion

router = APIRouter()


@router.get("/info", response_model=AppVersion)
async def info(settings: Settings = Depends(get_settings)):
    """Return app version information."""
    return AppVersion(version=settings.version, git_commit=settings.git_commit)


@router.get("/current_user", include_in_schema=False)
async def current_user(
    user_connection: UserConnection = Depends(get_app_user_connection),
):
    """Retrieve information about the current authorized user."""
    user_id = get_app_user_id(user_connection.connection)
    return {"user_id": int(user_id) if user_id is not None else None}
