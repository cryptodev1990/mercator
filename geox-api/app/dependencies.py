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
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session

from app import schemas
from app.core.config import Settings, get_settings
from app.core.security import VerifyToken, token_auth_scheme
from app.crud.user import create_or_update_user_from_bearer_data
from app.db.app_user import set_app_user_id
from app.db.session import SessionLocal, engine


async def get_engine() -> Engine:
    """Return an engine to generate connections to the app database."""
    return engine


async def get_connection(
    engine: Engine = Depends(get_engine),
) -> AsyncGenerator[Connection, None]:
    """Yield a connection with an open transaction."""
    # engine.begin() yields a connection and opens a transaction.
    with engine.begin() as conn:
        yield conn


async def get_session(
    conn: Connection = Depends(get_connection),
) -> AsyncGenerator[Session, None]:
    """Yield a SQLAlchemy session.

    Args:
        conn: Connection. The session will be bound to this connection, which is also expected to
            to have an open transaction.

    Yields:
        Generator[Session, None, None]: Yields a SQLAlchemy session. This session is
    """
    # Yield a session bound to a specific CONNECTION and TRANSACTION
    session = SessionLocal(bind=conn)
    return session


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
    session: Session = Depends(get_session),
    auth_jwt_payload: Dict[str, Any] = Depends(verify_token),
) -> schemas.User:
    """Return the current user from the bearer token.

    This function checks whether the JWT is valid and creates the user
    from the bearer information if they are now.
    """
    # TODO: I think it would be better if this returned the model user
    user = create_or_update_user_from_bearer_data(session, auth_jwt_payload)
    return user


# dependencies were split out over multiple functions so that each dependency would do one and only one thing
class UserSession(BaseModel):
    """User and database session to use in routes."""

    user: schemas.User
    session: Session

    class Config:  # noqa
        arbitrary_types_allowed = True


def set_app_user_settings(session: Session, user_id: int):
    session.execute(text("SET LOCAL ROLE app_user"))
    set_app_user_id(session, str(user_id), local=True)


async def get_app_user_session(
    user: schemas.User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserSession:
    """Configure database session for an authorized user.

    Adds a hook which inserts ``SET LOCAL app.user_id = :user_id``
    at the start of each transaction.

    """
    user_id = user.id

    set_app_user_settings(session, user_id)

    # Attaches a listener to the session object.
    # This will run after event start of a transaction, the "after_begin" event
    # https://docs.sqlalchemy.org/en/14/orm/events.html#sqlalchemy.orm.SessionEvents.after_begin

    # this is paranoid. It shouldn't be invoked because the session should be bound to a connection and a transaction
    @event.listens_for(session, "after_begin")
    def receive_after_begin(session, transaction, connection):
        set_app_user_settings(session, user_id)

    return UserSession(user=user, session=session)
