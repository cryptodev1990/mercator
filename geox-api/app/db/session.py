"""SQLAlchemy session objects and functions."""

from typing import Any, Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

SQLALCHEMY_DATABASE_URI: Any = get_settings().sqlalchemy_database_uri

engine = create_engine(SQLALCHEMY_DATABASE_URI)


def _set_default_app_user_id(dbapi_connection):
    with dbapi_connection.cursor() as c:
        c.execute("SET app.user_id TO DEFAULT")


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
    """Ensure that connections returned to the pool have app.user_id reeset default state."""
    # This is a redundancy in case somehow app.user_id was not cleared
    _set_default_app_user_id(dbapi_connection)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
"""SQLALchemy session to use in the app."""
