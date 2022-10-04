"""FastAPI dependencies.

See `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
"""
import os
from functools import lru_cache
from typing import Any, AsyncGenerator, Dict, Tuple, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4, BaseModel
from sqlalchemy import event, text
from sqlalchemy.engine import Connection, Engine

from app.core.config import Settings, get_settings
from app.core.security import VerifyToken, token_auth_scheme
from app.crud.organization import get_active_org_data
from app.crud.user import create_or_update_user_from_bearer_data
from app.db.app_user import set_app_user_id, set_app_user_org
from app.db.engine import engine
from app.db.osm import osm_engine
from app.schemas import UserOrganization


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
) -> UserOrganization:
    """Return the current user from the bearer token.

    This function checks whether the JWT is valid and creates the user
    from the bearer information if they are now.

    Returns:
        An object with the current user and their active organization.

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
        # Get the user's active org
        org = get_active_org_data(conn, user.id)
        # if no organization found, then raise an exception
        if org is None:
            raise HTTPException(403)
    return UserOrganization(user=user, organization=org)


class UserConnection(UserOrganization):
    """User, organization, and a database connecction all in one place."""

    connection: Connection


def set_app_user_settings(conn: Connection, user_id: int, org_id: UUID4):
    """Set up a SQLAlchemy session for RLS.

    - Set role to `app_user`
    - Set `app.user_id` setting to the ``user_id``
    - Set `app.user_org` setting to the ``org_id``

    """
    conn.execute(text("SET LOCAL ROLE app_user"))
    set_app_user_id(conn, user_id, local=True)
    set_app_user_org(conn, org_id, local=True)


async def get_app_user_connection(
    user_org: UserOrganization = Depends(get_current_user),
    conn=Depends(get_connection, use_cache=False),
) -> UserConnection:
    """Configure database session for an authorized user.

    Adds a hook which inserts ``SET LOCAL app.user_id = :user_id``
    at the start of each transaction.

    """
    set_app_user_settings(conn, user_org.user.id, user_org.organization.id)

    # start transaction
    return UserConnection(
        user=user_org.user, connection=conn, organization=user_org.organization
    )


@lru_cache(None)
def get_osm_engine() -> Engine:
    """Return OSM Engine."""
    if osm_engine is None:
        raise HTTPException(501, detail="OSM database not found.")
    return osm_engine


async def get_osm_conn(engine=Depends(get_osm_engine)) -> AsyncGenerator[Connection, None]:
    """Return a connection to an OSM database."""
    # TODO: should we disallow writes to it?
    with engine.begin() as conn:
        yield conn
