"""
FastAPI dependencies

See `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
"""
from multiprocessing import connection
from typing import Any, AsyncGenerator, Dict, Generator, Iterator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import event, text
from sqlalchemy.orm import Session

from app import schemas
from app.core.config import Settings, get_settings
from app.core.security import VerifyToken, token_auth_scheme
from app.crud.user import create_or_update_user_from_bearer_data
from app.db.app_user import set_app_user_id
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


# dependencies were split out over multiple functions so that each dependency would do one and only one thing
class UserSession(BaseModel):
    """User and database session to use in routes."""

    user: schemas.User
    session: Session

    class Config:  # noqa
        arbitrary_types_allowed = True


async def get_app_user_session(
    user: schemas.User = Depends(get_current_user),
    db_session: Session = Depends(get_db),
) -> UserSession:
    """Configure database session for an authorized user.

    Adds a hook which inserts ``SET LOCAL app.user_id = :user_id``
    at the start of each transaction.

    """
    user_id = user.id

    # Attaches a listener to the session object.
    # This will run after event start of a transaction, the "after_begin" event
    # https://docs.sqlalchemy.org/en/14/orm/events.html#sqlalchemy.orm.SessionEvents.after_begin

    @event.listens_for(db_session, "after_begin")
    def receive_after_begin(session, transaction, connection):
        session.execute(text("SET LOCAL ROLE app_user"))
        set_app_user_id(session, user_id, local=True)

    # Need to commit any remaining transactions prior to exiting
    db_session.commit()

    return UserSession(user=user, session=db_session)
