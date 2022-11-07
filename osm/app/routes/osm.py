"""Open Street Maps (OSM) routes."""
import logging
from typing import Any, Dict, Optional, Tuple

from fastapi import APIRouter, Depends, Query
from sqlalchemy.engine import Connection

from app.core.datatypes import Latitude, Longitude
from app.dependencies import get_conn
from app.parser import parse_query
from app.schemas import BaseModel

router = APIRouter()

logger = logging.getLogger(__name__)


class OsmSearchResponse(BaseModel):
    """Response for OSM search."""

    query: str
    parsed: Optional[Dict[str, Any]]


# pylint: disable=unused-argument
@router.get("/search", response_model=OsmSearchResponse)
async def get_shapes_from_osm(
    query: str = Query(...),
    bbox: Optional[Tuple[Latitude, Longitude, Latitude, Longitude]] = Query(None),
    conn: Connection = Depends(get_conn),
) -> OsmSearchResponse:
    """Get shapes from OSM by amenity."""
    parsed = parse_query(query)
    return OsmSearchResponse(query=query, parsed=parsed)


# pylint: enable=unused-argument
