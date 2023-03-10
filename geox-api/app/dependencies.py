"""FastAPI dependencies.

See `FastAPI dependency injection <https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/>`__.
"""
import logging
from functools import lru_cache
from http import HTTPStatus
from typing import Any, AsyncGenerator, Dict, Optional, Protocol, cast

import walrus
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4  # pylint: disable=no-name-in-module
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.core.security import VerifyToken, token_auth_scheme
from app.core.stats import time_db_query
from app.crud.organization import get_active_organization
from app.crud.user import create_or_update_user_from_bearer_data
from app.db.app_user import set_app_user_id, set_app_user_org
from app.db.engine import engine
from app.db.osm import osm_engine
from app.schemas import User, UserOrganization
from app.schemas.organizations import Organization, StripeSubscriptionStatus

logger = get_logger(__name__)


async def get_engine() -> Engine:
    """Return an engine to generate connections to the app database."""
    return engine


async def get_connection(
    engine: Engine = Depends(get_engine),  # pylint: disable=redefined-outer-name
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


class Cache(Protocol):
    """Abstract protocol for what methods a cache needs to contain."""

    def set(self, key: Any, value: Any, timeout: Optional[Any] = None) -> Any:
        ...

    def get(self, key: Any, default: Optional[Any] = None) -> Any:
        ...

    def delete(self, key: Any) -> Any:
        ...


@lru_cache()
def get_cache() -> Optional[Cache]:
    settings = get_settings()
    opts = settings.cache
    conn = settings.redis_connection
    if opts.enabled:
        try:
            db = walrus.Database(
                host=conn.host,
                port=conn.port,
                db=int(conn.path[1:]) if conn.path else None,
                password=conn.password,
            )
            cache: walrus.Cache = db.cache(default_timeout=opts.timeout)
            return cache
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Error initializing the cache: %s", exc)
    return None


def _current_user_key_fn(sub_id: str) -> str:
    return f"app:cache:user_org:{sub_id}"


async def get_current_user(
    engine: Engine = Depends(get_engine),  # pylint: disable=redefined-outer-name
    auth_jwt_payload: Dict[str, Any] = Depends(verify_token),
    cache: Optional[Cache] = Depends(get_cache),
) -> User:
    """Return the current user from the bearer token.

    This function checks whether the JWT is valid and creates the user
    from the bearer information if they are now.

    Returns:
        An object with the current user

    """
    # this function does not use the same connection as used later because it
    # needs / should commit it's result prior to the logic in the request.
    # conceptualy the authentication/authorization step here is separate from
    # the request logic.
    #
    # get_current_user and get_current_usr_org are split into two functions
    # because it allows skipping opening db connections and using cache values
    # prior to trying to open a database connection.
    sub_id = auth_jwt_payload.get("sub")
    # TODO: this error checking may be redundant - verify auth_jwt_payload should have
    # raised an exception if something were wrong.
    if sub_id is None:
        raise HTTPException(401)
    key = _current_user_key_fn(sub_id)
    user = None
    if cache:
        try:
            user = cache.get(key)
            try:
                assert isinstance(user, User)
                logger.debug("User retrieved %s from cache.", sub_id)
            except AssertionError:
                logger.warning("Cache error: value of %s is invalid", key)
                cache.set(key, None)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Cache error: %s", exc)
    if user is None:
        logger.debug("User %s not retrieved from cache.", sub_id)
        with engine.begin() as conn:
            user = create_or_update_user_from_bearer_data(conn, auth_jwt_payload)
            if user is None:
                raise HTTPException(403)
            if cache:
                cache.set(key, user)
    return cast(User, user)


def _current_user_org_key_fn(user_id: int) -> str:
    return f"app:cache:user_org:{user_id}"


async def get_current_user_org(
    engine: Engine = Depends(get_engine),  # pylint: disable=redefined-outer-name
    user: User = Depends(get_current_user),
    cache: Optional[Cache] = Depends(get_cache),
) -> UserOrganization:
    user_id = user.id
    if user_id is None:
        raise HTTPException(403)
    key = _current_user_org_key_fn(user_id)
    org = None
    if cache:
        try:
            org = cache.get(key)
            try:
                assert isinstance(org, Organization)
                logger.debug(
                    "Organization for user %s retried from cache %s", user_id, key
                )
            except AssertionError:
                logger.warning("Cache error: value of %s is invalid", key)
                cache.set(key, None)
        except Exception as exc:  # pylint: disable=broad-except
            logger.warning("Cache error: %s", exc)
    if org is None:
        with engine.begin() as conn:
            org = get_active_organization(conn, user_id)
        # if no organization found, then raise an exception
        if org is None:
            raise HTTPException(403)
        if cache:
            cache.set(key, org)
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
    with time_db_query("set_app_user_settings"):
        conn.execute(text("SET LOCAL ROLE app_user"))
    set_app_user_id(conn, user_id, local=True)
    set_app_user_org(conn, org_id, local=True)


async def get_app_user_connection(
    user_org: UserOrganization = Depends(get_current_user_org),
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
        raise HTTPException(HTTPStatus.NOT_IMPLEMENTED, detail="OSM database not found.")
    return osm_engine


async def get_osm_conn(
    engine=Depends(get_osm_engine),  # pylint: disable=redefined-outer-name
) -> AsyncGenerator[Connection, None]:
    """Return a connection to an OSM database."""
    # TODO: should we disallow writes to it?
    with engine.begin() as conn:
        yield conn


async def verify_subscription(
    user_org: UserOrganization = Depends(get_current_user_org),
    settings: Settings = Depends(get_settings),
) -> bool:
    """Verify that the user is user is a member of a Mercator-subscribed organization."""

    if settings.skip_stripe:
        return True

    if user_org.organization.subscription_whitelist:
        return True

    org = user_org.organization
    if not org.stripe_subscription_id:
        raise HTTPException(402, detail="No subscription found.")
    if not org.stripe_subscription_status:
        raise HTTPException(402, detail="Subscription requires payment.")
    if org.stripe_subscription_status not in (
        StripeSubscriptionStatus.active,
        StripeSubscriptionStatus.trialing,
    ):
        raise HTTPException(402, detail="Subscription expired.")
    return True
