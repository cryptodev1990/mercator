"""FastAPI dependencies.

See `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
"""
from typing import Any, AsyncGenerator, Dict, Union

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


async def get_session() -> AsyncGenerator[Session, None]:
    """Yield a SQLAlchemy session.

    Args:
        conn: Connection. The session will be bound to this connection, which is also expected to
            to have an open transaction.

    Yields:
        Generator[Session, None, None]: Yields a SQLAlchemy session. This session is
    """
    # Yield a session bound to a specific CONNECTION and TRANSACTION
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


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
    session: Session = Depends(get_session, use_cache=False),
    auth_jwt_payload: Dict[str, Any] = Depends(verify_token),
) -> schemas.User:
    """Return the current user from the bearer token.

    This function checks whether the JWT is valid and creates the user
    from the bearer information if they are now.
    """
    # TODO: I think it would be better if this returned the model user
    with session.begin():
        user = create_or_update_user_from_bearer_data(session, auth_jwt_payload)
    return user


# dependencies were split out over multiple functions so that each dependency would do one and only one thing
class UserSession(BaseModel):
    """User and database session to use in routes."""

    user: schemas.User
    session: Session

    class Config:  # noqa
        arbitrary_types_allowed = True


def set_app_user_settings(session: Union[Session, Connection], user_id: int):
    session.execute(text("SET LOCAL ROLE app_user"))
    set_app_user_id(session, str(user_id), local=True)


async def get_app_user_session(
    user: schemas.User = Depends(get_current_user),
    session: Session = Depends(get_session, use_cache=False),
) -> AsyncGenerator[UserSession, None]:
    """Configure database session for an authorized user.

    Adds a hook which inserts ``SET LOCAL app.user_id = :user_id``
    at the start of each transaction.

    """
    user_id = user.id

    # Attaches a listener to the session object.
    # This will run after event start of a transaction, the "after_begin" event
    # https://docs.sqlalchemy.org/en/14/orm/events.html#sqlalchemy.orm.SessionEvents.after_begin

    # this is paranoid. It shouldn't be invoked because the session should be bound to a connection and a transaction
    @event.listens_for(session, "after_begin")
    def receive_after_begin(session, transaction, connection):
        set_app_user_settings(session, user_id)

    # start transaction
    with session.begin():
        yield UserSession(user=user, session=session)


"""FastAPI dependencies.

See `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
"""



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


async def get_current_user_conn(
    conn: Connection = Depends(get_connection, use_cache=False),
    auth_jwt_payload: Dict[str, Any] = Depends(verify_token),
) -> schemas.User:
    """Return the current user from the bearer (connection version).

    This function checks whether the JWT is valid and creates the user
    from the bearer information if they are now.
    """
    # TODO: I think it would be better if this returned the model user
    user = create_or_update_user_from_bearer_data(conn, auth_jwt_payload)
    return user


# dependencies were split out over multiple functions so that each dependency would do one and only one thing
class UserConnection(BaseModel):
    """User and database connection to use in API routes."""

    user: schemas.User
    connection: Connection

    class Config:  # noqa
        arbitrary_types_allowed = True


async def get_app_user_connection(
    user: schemas.User = Depends(get_current_user),
    conn: Connection = Depends(get_connection, use_cache=False),
) -> UserConnection:
    """Configure database conn for an authorized user.

    Adds a hook which inserts ``SET LOCAL app.user_id = :user_id``
    at the start of each transaction.

    """
    user_id = user.id

    set_app_user_settings(conn, user_id)

    # Attaches a listener to the conn object.
    # This will run after event start of a transaction, the "after_begin" event
    # https://docs.sqlalchemy.org/en/14/orm/events.html#sqlalchemy.orm.SessionEvents.after_begin

    return UserConnection(user=user, connection=conn)
