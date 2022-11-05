from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import UUID4  # pylint: disable=no-name-in-module

from app.core.datatypes import Latitude, Longitude
from app.crud.shape import get_shape_metadata_matching_search, select_shape_metadata
from app.dependencies import (
    UserConnection,
    get_app_user_connection,
    verify_subscription,
    verify_token,
)
from app.schemas import GeoShapeMetadata, ViewportBounds

router = APIRouter(
    tags=["geofencer", "shape-metadata"],
    dependencies=[Depends(verify_token), Depends(verify_subscription)],
)


DEFAULT_LIMIT = 25


@router.get(
    "/geofencer/shape-metadata/bbox",
    response_model=List[GeoShapeMetadata],
    tags=["shape-metadata"],
)
def _get_shape_metadata__bbox(
    min_x: float = Query(ge=-180, le=180),
    min_y: float = Query(ge=-90, le=90),
    max_x: float = Query(ge=-180, le=180),
    max_y: float = Query(ge=-90, le=90),
    user_conn: UserConnection = Depends(get_app_user_connection),
    offset: int = Query(default=0, title="Item offset", ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, title="Number of shapes to retrieve", ge=1),
) -> List[GeoShapeMetadata]:
    """Get shape metadata by bounding box."""
    bbox = ViewportBounds(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)
    shapes = list(
        select_shape_metadata(user_conn.connection, bbox=bbox, limit=limit, offset=offset)
    )
    return shapes


@router.get(
    "/geofencer/shape-metadata/search",
    response_model=List[GeoShapeMetadata],
    tags=["shape-metadata"],
)
def _get_shape_metadata__search(
    query: str,
    offset: int = Query(default=0, title="Item offset", ge=0),
    limit: int = Query(default=DEFAULT_LIMIT, title="Number of shapes to retrieve", ge=1),
    user_conn: UserConnection = Depends(get_app_user_connection),
) -> List[GeoShapeMetadata]:
    """Get shape metadata by bounding box."""
    shapes = get_shape_metadata_matching_search(
        user_conn.connection, query, limit, offset
    )
    return shapes


@router.get(
    "/geofencer/shape-metadata",
    response_model=List[GeoShapeMetadata],
    tags=["shape-metadata"],
)
def _get_shape_metadata(
    user_conn: UserConnection = Depends(get_app_user_connection),
    # Query(default=0, title="Item offset", ge=0),
    offset: int = Query(default=0),
    limit: int = Query(default=DEFAULT_LIMIT),
    user: Optional[bool] = Query(
        default=None,
        title="Get shapes for a user",
        description="If TRUE, then only return shapes of the requesting user.",
    ),
    namespace: Optional[UUID4] = Query(default=None, title="Namespace id."),
    shape_ids: Optional[List[UUID4]] = Query(default=None, title="Shape ids."),
    bbox: Optional[Tuple[Longitude, Latitude, Longitude, Latitude]] = Query(
        default=None, title="Bounding box (min x, min y, max x, max y)"
    ),
) -> List[GeoShapeMetadata]:
    """Get all shape metadata with pagination."""
    bbox_obj: Optional[ViewportBounds]
    if bbox:
        try:
            bbox_obj = ViewportBounds.from_list(bbox)
        except (ValueError, TypeError):
            raise HTTPException(422, "Invalid bbox") from None
    else:
        bbox_obj = None
    user_id = user_conn.user.id if user else None
    return list(
        select_shape_metadata(
            user_conn.connection,
            namespace_id=namespace,
            limit=limit,
            offset=offset,
            user_id=user_id,
            ids=shape_ids,
            bbox=bbox_obj,
        )
    )
