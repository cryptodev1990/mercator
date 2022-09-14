"""
FastAPI dependencies

See `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
"""
from typing import Any, AsyncGenerator, Dict, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app import schemas
from app.core.config import Settings, get_settings
from app.core.security import VerifyToken, token_auth_scheme
from app.crud.new.user import create_or_update_user_from_bearer_data
from app.db.app_user import set_app_user_id, unset_app_user_id
from app.db.session import engine
from app.schemas.common import BaseModel


def get_db_conn() -> Generator[Connection, None, None]:
    with engine.begin() as conn:
        yield conn


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


def get_current_user(
    conn: Connection = Depends(get_db_conn),
    auth_jwt_payload: Dict[str, Any] = Depends(verify_token),
) -> schemas.User:
    """Return the current user from the bearer token.

    This function checks whether the JWT is valid and creates the user
    from the bearer information if they are now.
    """
    # TODO: I think it would be better if this returned the model user
    user = create_or_update_user_from_bearer_data(conn, auth_jwt_payload)
    return user


# dependencies were split out over multiple functions so that each dependency would do one and only one thing
class UserConnection(BaseModel):
    """User and database session to use in routes."""

    user: schemas.User
    connection: Connection


async def get_user_connection(
    user: schemas.User = Depends(get_current_user),
    conn: Connection = Depends(get_db_conn),
) -> Generator[UserConnection, None, None]:
    """Configure database session for an authorized user.

    Adds a hook which inserts ``SET LOCAL app.user_id = :user_id``
    at the start of each transaction.

    """
    user_id = user.id

    # Attaches a listener to the session object.
    # This will run after event start of a transaction, the "after_begin" event
    # https://docs.sqlalchemy.org/en/14/orm/events.html#sqlalchemy.orm.SessionEvents.after_begin

    # This is inside a transaction
    conn.execute(text("SET LOCAL ROLE app_user"))
    set_app_user_id(conn, str(user_id), local=True)

    yield UserConnection(user=user, connection=conn)
