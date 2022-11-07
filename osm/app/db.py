"""SQLAlchemy engine for the the app database."""
import logging
from typing import Any, Dict

from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, MetaData, String, Table
from sqlalchemy.dialects.postgresql import JSONB
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
    params: Dict[str, Any] = {"future": True, "pool_pre_ping": True}
    params.update(settings.db.options.dict())
    params.update(kwargs)
    engine_: AsyncEngine = create_async_engine(uri, **params)
    return engine_


engine = create_app_engine()

osm = Table(
    "osm",
    metadata,
    Column("osm_id", Integer, primary_key=True),
    Column("osm_type", String(1), nullable=False),
    Column("tags", JSONB),
    Column("attrs", JSONB),
    Column("geom", Geometry),
)
