"""SQLAlchemy engine for the the app database."""

import logging
from typing import Any, Dict

from sqlalchemy.ext.asyncio import ( # type: ignore
    AsyncEngine,
    create_async_engine,
)

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


def create_app_engine(settings: Settings = get_settings(), **kwargs: Any) -> AsyncEngine:
    """Return an engine for the app database.

    Args:
        settings: App settings used to setup the engine. Uses
        ``sqlalchemy_database_uri``.

    Returns:
        A SQLAlchemy engine for connections to the app database.

    """
    uri = settings.db.url.get_secret_value()
    params: Dict[str, Any] = {"future": True, "pool_pre_ping": True}
    params.update(settings.db.options.dict())
    params.update(kwargs)
    engine_ = create_async_engine(uri, **params)
    return engine_


engine = create_app_engine()
