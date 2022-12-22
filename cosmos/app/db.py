"""SQLAlchemy engine for the the app database."""
import logging
from typing import Any, Dict

from geoalchemy2 import Geometry
from sqlalchemy import Computed  # type: ignore
from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine  # type: ignore

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

metadata: MetaData = MetaData()


def create_app_engine(settings: Settings = get_settings(), **kwargs: Any) -> AsyncEngine:
    """Return an engine for the app database.

    Args:
        settings: App settings used to setup the engine. Uses
        ``sqlalchemy_database_uri``.

    Returns:
        A SQLAlchemy engine for connections to the app database.

    """
    uri = settings.db.url.get_secret_value()
    opts = {
        k: getattr(settings.db.options, k)
        for k in ("echo", "echo_pool", "pool_recycle", "pool_size", "max_overflow", "pool_timeout")
    }
    params: Dict[str, Any] = {
        "future": True,
        "pool_pre_ping": True,
        **opts,
        "connect_args": {
            "server_settings": {
                "session_preload_libraries": "auto_explain",
                "auto_explain.log_min_duration": "1000",
                "auto_explain.log_format": "text",
            }
        },
    }
    params.update(kwargs)
    engine_: AsyncEngine = create_async_engine(uri, **params)

    return engine_


engine = create_app_engine()

osm = Table(
    "osm",
    metadata,
    Column("id", String, primary_key=True),
    Column("osm_id", Integer, primary_key=True),
    Column("osm_type", String(1)),
    Column("tags", JSONB()),
    Column("geom", Geometry(srid=4326)),
    Column("fts", TSVECTOR, Computed("to_tsvector('english', tags)")),
    Column("tags_text", String()),
)
