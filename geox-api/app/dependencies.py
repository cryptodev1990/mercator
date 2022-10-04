"""FastAPI dependencies.

See `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
"""
from functools import lru_cache
import os

from typing import Any, AsyncGenerator, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from app import schemas
from app.core.config import Settings, get_settings
from app.core.security import VerifyToken, token_auth_scheme
from app.crud.user import create_or_update_user_from_bearer_data
from app.db.app_user import set_app_user_id
from app.db.engine import engine
from app.db.osm import osm_engine


async def get_engine() -> Engine:
    """Return an engine to generate connections to the app database."""
    return engine


async def get_connection(
    engine: Engine = Depends(get_engine),
) -> AsyncGenerator[Connection, None]:
    """Yield a connection with an open transaction."""
    # engine.begin() yields a connection and also opens a transaction.
    # the context manager will close the connection and transaction
    with engine.begin() as conn:
        yield conn


async def verify_token(
    token: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
    settings: Settings = Depends(get_settings),
) -> Dict[str, Any]:
    # # TODO airplane mode hack, do we want some formal way of enabling this?
    # if True:
    #     return {
    #         "user_id": 1,
    #         "email": "duber@mercator.tech",
    #         "sub": "google-oauth2|106524875829152250066",
    #         "given_name": "Andrew",
    #         "family_name": "Duberstein",
    #         "nickname": "duber",
    #         "name": "Andrew Duberstein",
    #         "picture": 'https://lh3.googleusercontent.com/a/ALm5wu1LKKw_sg52wMdTVMINtL62g1XKwnXg-p6GCctm=s96-c',
    #         "locale": 'en',
    #         "updated_at": '2022-09-20 10:07:13.805',
    #         "email_verified": 'True',
    #         "iss": 'https://dev-w40e3mxg.us.auth0.com/',
    #     }
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
    engine: Engine = Depends(get_engine),
    auth_jwt_payload: Dict[str, Any] = Depends(verify_token),
) -> schemas.User:
    """Return the current user from the bearer (connection version).

    This function checks whether the JWT is valid and creates the user
    from the bearer information if they are now.
    """
    # this function does not use the same connection as used later because it
    # needs / should commit it's result prior to the logic in the request.
    # conceptualy the authentication/authorization step here is separate from
    # the request logic.
    #
    # conn: Connection = Depends(get_connection, cache=False) is not used
    # because the way FastAPI dependencies work would keep the connection open
    # until the end of the request so each request would use 2 connections.
    with engine.begin() as conn:
        user = create_or_update_user_from_bearer_data(conn, auth_jwt_payload)
    return user


# dependencies were split out over multiple functions so that each dependency would do one and only one thing
class UserConnection(BaseModel):
    """User and database connection to use in API routes."""

    user: schemas.User
    connection: Connection

    class Config:  # noqa
        arbitrary_types_allowed = True


def set_app_user_settings(conn: Connection, user_id: int) -> None:
    conn.execute(text("SET LOCAL ROLE app_user"))
    set_app_user_id(conn, user_id, local=True)


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


@lru_cache(None)
def get_osm_engine() -> Engine:
    """Return OSM Engine."""
    if osm_engine is None:
        raise HTTPException(501, detail="OSM database not found.")
    return osm_engine


async def get_osm_conn(engine=Depends(get_osm_engine)) -> AsyncGenerator[Connection, None]:
    """Return a connection to an OSM database."""
    # TODO: should we disallow writes to it?
    with engine.begin():
        yield engine
