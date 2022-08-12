"""
FastAPI dependencies

See `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
"""
from typing import Any, AsyncGenerator, Dict, Generator, Iterator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import schemas
from app.core.config import Settings, get_settings
from app.core.security import VerifyToken, token_auth_scheme
from app.crud.user import create_or_update_user_from_bearer_data
from app.db.session import SessionLocal


async def get_db() -> AsyncGenerator[Session, None]:
    """
    Yields a SQLAlchemy session.

    Yields:
        Generator[Session, None, None]: Yields a SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def verify_token(
    token: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    """Verify a JWT token."""
    # When should this return 401 vs. 403 exceptions
    exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
    )
    payload = VerifyToken(token.credentials, settings).verify()
    if payload.get("status") == "error":
        raise exception
    return payload


async def get_current_user(
    db_session: Session = Depends(get_db),
    auth_jwt_payload: Dict[str, Any] = Depends(verify_token),
) -> schemas.User:
    """
    Returns the current user from the bearer token

    This function checks whether the JWT is valid and creates the user
    from the bearer information if they are now.
    """
    # TODO: I think it would be better if this returned the model user
    user = create_or_update_user_from_bearer_data(db_session, auth_jwt_payload)
    return user


async def set_current_user_session(
    user: schemas.User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> AsyncGenerator[Session, None]:
    """Get SQLAlchemy session and user information"""
    # NOTE: Dependencies are cached by sqlalchemy, so session settings hopefully aren't an issue
    try:
        db_session.execute("SET LOCAL app.userId = :user_id", {"user_id": user.id})
        yield db_session
    finally:
        db_session.execute("SET app.userId = DEFAULT")


# dependencies were split out over multiple functions so that each dependency would do one and only one thing


class UserSession(BaseModel):
    """User and database session to use in routes."""

    def __init__(
        self,
        user: schemas.User = Depends(get_current_user),
        db_session: Session = Depends(get_db),
    ):
        self.user = user
        self.session = db_session


# def get_user_and_session(user: schemas.User = Depends(get_current_user),
#                          db_session: Session = Depends(get_db)):
#     """Returns the user information and a customized database session."""
#     return UserSession(user=user, session=db_session)
