from typing import List

from fastapi import APIRouter, Depends, Query, Request, Response
from morecantile.commons import Tile
from morecantile.models import TileMatrixSet
from pydantic import UUID4  # pylint: disable=no-name-in-module
from timvt.dependencies import LayerParams, TileMatrixSetParams, TileParams
from timvt.factory import TILE_RESPONSE_PARAMS
from timvt.layer import Layer
from timvt.resources.enums import MimeTypes

from app.dependencies import get_current_user_org, verify_token
from app.schemas.user_organizations import UserOrganization

router = APIRouter(tags=["geofencer"])

# Borrowed from https://github.com/developmentseed/timvt/blob/master/timvt/factory.py#L112


@router.get(
    "/backsplash/{layer}/{z}/{x}/{y}",
    **TILE_RESPONSE_PARAMS,
    tags=["geofencer"],
    dependencies=[Depends(verify_token)]
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
    # Can use get_current_user_org instead of get_user_connection because currently
    # the tiler uses a separate connection pool
    user_org: UserOrganization = Depends(get_current_user_org),
):
    """Get a tile of shape."""
    org_id = user_org.organization.id
    pool = request.app.state.pool
    kwargs = {"organization_id": org_id, "namespace_ids": namespace_ids}

    content = await layer.get_tile(pool, tile, tms, **kwargs)

    return Response(bytes(content), media_type=MimeTypes.pbf.value)


# SUPPORT CENSUS DEMO
# NOTE this is NOT behind authentication
@router.get(
    "/backsplash/zcta/{layer}/{z}/{x}/{y}",
    **TILE_RESPONSE_PARAMS,
    tags=["geofencer"],
)
async def get_zcta_shape_tile(
    request: Request,
    tile: Tile = Depends(TileParams),
    tms: TileMatrixSet = Depends(TileMatrixSetParams),
    layer: Layer = Depends(LayerParams),
    # Can use get_current_user_org instead of get_user_connection because currently
    # the tiler uses a separate connection pool
    # user_org: UserOrganization = Depends(get_current_user_org),
):
    """Get the US census ZCTAs served"""
    ONE_VALID_NAMESPACE_UUID = '61aa8970-6102-4ecb-b7aa-be8f0080a8f5'
    MERCATOR_ORG_UUID = 'e6cef492-5069-46d3-8431-fda523caf2f6'
    pool = request.app.state.pool
    kwargs = {"organization_id": MERCATOR_ORG_UUID, "namespace_ids": [ONE_VALID_NAMESPACE_UUID]}

    content = await layer.get_tile(pool, tile, tms, **kwargs)

    return Response(bytes(content), media_type=MimeTypes.pbf.value)
