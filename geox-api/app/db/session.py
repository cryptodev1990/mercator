"""SQLAlchemy session objects and functions."""

import logging
from asyncio.log import logger
from functools import lru_cache
from typing import Any, Dict, Optional

import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

def _set_default_app_user_id(dbapi_connection):
    # The dbapi_connection is the engine connection
    # instance(dbapi_connection, 'psycopg2.extensions.cursor')
    with dbapi_connection.cursor() as c:
        # instance(c, 'psycopg2.extensions.cursor')
        stmt = "SET app.user_id TO DEFAULT"
        c.execute(stmt)


def create_app_engine(settings: Settings = get_settings(), **kwargs) -> Engine:
    """Return an engine for the app database.

    Args:
        settings: App settings used to setup the engine. Uses
        ``sqlalchemy_database_uri``.

    Returns:
        A SQLAlchemy engine for connections to the app database.

    """
    uri = settings.sqlalchemy_database_uri
    params: Dict[str, Any] = {"future": True, "pool_pre_ping": True}

    params.update(kwargs)
    engine = sa.create_engine(uri, **params)

    # Adds events to set/reset values of app_user_id settings
    # Called when a connection is created
    # https://docs.sqlalchemy.org/en/14/core/events.html#sqlalchemy.events.PoolEvents.connect
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_connection, connection_record):
        """Ensure connections have the setting app.user_id defined."""
        _set_default_app_user_id(dbapi_connection)

    # Called when a connection is checked out from the pool - before a session uses it
    @event.listens_for(engine, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        """Ensure that connections checked from the pool have app.user_id in the default state."""
        # This is a redundancy in case somehow app.user_id was not cleared
        _set_default_app_user_id(dbapi_connection)

    # engine returned to pool - after a session uses it
    @event.listens_for(engine, "reset")
    def receive_reset(dbapi_connection, connection_record):
        """Ensure that connections returned to the pool have app.user_id reset default state."""
        # This is a redundancy in case somehow app.user_id was not cleared
        _set_default_app_user_id(dbapi_connection)

    return engine


engine = create_app_engine()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
