"""SQLAlchemy session objects and functions."""

import logging
from asyncio.log import logger
from typing import Any, Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URI: Any = get_settings().sqlalchemy_database_uri
OSM_DATABASE_URI: Any = get_settings().sqlalchemy_osm_database_uri

engine = create_engine(SQLALCHEMY_DATABASE_URI, future=True)


def _set_default_app_user_id(dbapi_connection):
    # The dbapi_connection is the engine connection
    # instance(dbapi_connection, 'psycopg2.extensions.cursor')
    with dbapi_connection.cursor() as c:
        # instance(c, 'psycopg2.extensions.cursor')
        stmt = "SET app.user_id TO DEFAULT"
        c.execute(stmt)


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


OsmSessionLocal: Optional[sessionmaker] = None
osm_engine: Optional[Engine] = None
if OSM_DATABASE_URI:
    osm_engine = create_engine(OSM_DATABASE_URI)
    OsmSessionLocal = sessionmaker(bind=osm_engine, future=True)
else:
    logger.warning("OSM_DATABASE_URI is not set, OSM features will be disabled")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
