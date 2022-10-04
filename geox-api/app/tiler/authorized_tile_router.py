from fastapi import APIRouter, Depends, Request, Response
from morecantile import Tile, TileMatrixSet
from timvt.dependencies import LayerParams, TileMatrixSetParams, TileParams
from timvt.factory import TILE_RESPONSE_PARAMS
from timvt.layer import Layer
from timvt.resources.enums import MimeTypes

from app.crud.organization import get_active_org
from app.dependencies import UserConnection, get_app_user_connection, verify_token

router = APIRouter(tags=["geofencer"], dependencies=[Depends(verify_token)])

# Borrowed from https://github.com/developmentseed/timvt/blob/master/timvt/factory.py#L112


@router.get(
    "/backsplash/{layer}/{z}/{x}/{y}/{cache_key}",
    **TILE_RESPONSE_PARAMS,
    tags=["geofencer"],
)
async def get_shape_tile(
    request: Request,
    tile: Tile = Depends(TileParams),
    tms: TileMatrixSet = Depends(TileMatrixSetParams),
    layer: Layer = Depends(LayerParams),
    user_conn: UserConnection = Depends(get_app_user_connection),
    cache_key: int = 0,
):
    """Get a tile of shape

    Cache key is used to keep the same result for immutable functions
    On each material change (create/update/delete) for shapes
    we bump the cache ID
    """
    org_id = get_active_org(user_conn.connection, user_conn.user.id)
    pool = request.app.state.pool
    kwargs = {"organization_id": org_id, "cache_key": cache_key}

    content = await layer.get_tile(pool, tile, tms, **kwargs)

    return Response(bytes(content), media_type=MimeTypes.pbf.value)
