from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request, Response
from morecantile import Tile, TileMatrixSet
from pydantic import UUID4, create_model
from timvt.dependencies import LayerParams, TileMatrixSetParams, TileParams
from timvt.factory import TILE_RESPONSE_PARAMS
from timvt.layer import Layer
from timvt.resources.enums import MimeTypes

from app.crud.organization import get_active_organization
from app.dependencies import UserConnection, get_app_user_connection, verify_token

router = APIRouter(tags=["geofencer"], dependencies=[Depends(verify_token)])

# Borrowed from https://github.com/developmentseed/timvt/blob/master/timvt/factory.py#L112


@router.get(
    "/backsplash/{layer}/{z}/{x}/{y}",
    **TILE_RESPONSE_PARAMS,
    tags=["geofencer"],
)
async def get_shape_tile(
    request: Request,
    namespace_ids: List[UUID4] = Query(
        None,
        description="List of namespaces to query. If not included, defaults to all namespaces",
    ),
    tile: Tile = Depends(TileParams),
    tms: TileMatrixSet = Depends(TileMatrixSetParams),
    layer: Layer = Depends(LayerParams),
    user_conn: UserConnection = Depends(get_app_user_connection),
):
    """Get a tile of shape."""
    org_id = user_conn.organization.id
    pool = request.app.state.pool
    kwargs = {"organization_id": org_id, "namespace_ids": namespace_ids}

    content = await layer.get_tile(pool, tile, tms, **kwargs)

    return Response(bytes(content), media_type=MimeTypes.pbf.value)
