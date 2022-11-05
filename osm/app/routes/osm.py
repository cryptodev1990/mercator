"""Open Street Maps (OSM) routes."""
import logging
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, Query
from sqlalchemy.engine import Connection

from app.core.datatypes import Latitude, Longitude
from app.dependencies import get_conn

router = APIRouter(tags=["osm"])

logger = logging.getLogger(__name__)

# pylint: disable=unused-argument
@router.get("/osm")
async def get_shapes_from_osm(
    query: str = Query(...),
    bbox: Optional[Tuple[Latitude, Longitude, Latitude, Longitude]] = Query(None),
    conn: Connection = Depends(get_conn),
) -> None:
    """Get shapes from OSM by amenity."""


# pylint: enable=unused-argument
