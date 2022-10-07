"""Open Street Map (OSM) sessions."""
import logging
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


def create_osm_engine(settings: Settings = get_settings()) -> Optional[Engine]:
    osm_database_uri = settings.sqlalchemy_osm_database_uri
    if osm_database_uri is None:
        logger.warning("OSM_DATABASE_URI is not set, OSM features will be disabled")
        return None
    return create_engine(osm_database_uri, pool_pre_ping=True, future=True)


osm_engine = create_osm_engine()
