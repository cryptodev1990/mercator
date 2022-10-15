from typing import List

from fastapi import APIRouter, Depends, Query

from app.crud.shape import (
    get_shape_metadata_by_bounding_box,
    get_shape_metadata_matching_search,
    select_shape_metadata,
)
from app.dependencies import UserConnection, get_app_user_connection, verify_token
from app.schemas import GeoShapeMetadata, ViewportBounds

router = APIRouter(
    tags=["geofencer", "shape-metadata"], dependencies=[Depends(verify_token)]
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
    limit: int = Query(
        default=DEFAULT_LIMIT, title="Number of shapes to retrieve", ge=1
    ),
) -> List[GeoShapeMetadata]:
    """Get shape metadata by bounding box."""
    bbox = ViewportBounds(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)
    shapes = get_shape_metadata_by_bounding_box(
        user_conn.connection, bbox, limit, offset
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
    limit: int = Query(
        default=DEFAULT_LIMIT, title="Number of shapes to retrieve", ge=1
    ),
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
    # namespace: Optional[UUID4] = Query(default=None),
    offset: int = Query(default=0),  # Query(default=0, title="Item offset", ge=0),
    limit: int = Query(default=DEFAULT_LIMIT),
) -> List[GeoShapeMetadata]:
    """Get all shape metadata with pagination."""
    return list(
        select_shape_metadata(
            user_conn.connection,
            # namespace_id=namespace,
            limit=limit,
            offset=offset,
        )
    )
