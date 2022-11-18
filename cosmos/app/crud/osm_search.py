"""OSM search functions."""
import logging
from enum import Enum
from typing import Any, AsyncGenerator, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql import Select

from app.core.datatypes import ViewportBounds
from app.db import osm as osm_table
from app.parser import InSpRelation, SpatialRelation, func, parse_query

logger = logging.getLogger(__name__)


class MapProjection(int, Enum):
    WGS84 = 4326
    WEB_MERCATOR = 3857


from sqlalchemy.sql import ColumnElement


def _viewport_to_sql_bbox(
    bbox: ViewportBounds, proj: MapProjection = MapProjection.WGS84
) -> ColumnElement:
    """Return a SQL bbox."""
    return func.ST_MakeEnvelope(bbox.min_x, bbox.min_y, bbox.max_x, bbox.max_y, proj)


def _sql_bbox_array(c: ColumnElement) -> ColumnElement:
    """Return a SQL bbox."""
    return func.jsonb_build_array(
        func.ST_XMin(c),
        func.ST_YMin(c),
        func.ST_XMax(c),
        func.ST_YMax(c),
    )


def _to_geojson(geom: ColumnElement, tags: ColumnElement) -> ColumnElement:
    return func.jsonb_build_object(
        "type",
        "Feature",
        "geometry",
        func.St_AsGeoJSON(geom),
        "properties",
        func.jsonb_build_object("osm_tags", tags),
        "bbox",
        _sql_bbox_array(geom),
    )


def create_query(
    *,
    figure: str,
    ground: str,
    relation: SpatialRelation,
    limit: Optional[int] = 20,
    top_n_figure: Optional[int] = 10,
    top_n_ground: Optional[int] = 10,
    bbox: Optional[ViewportBounds] = None,
    offset: Optional[int] = 0,
) -> Select:

    sel_figure = (
        select([osm_table.c.tags, osm_table.c.geom])
        .where(osm_table.c.fts.op("@@")(func.websearch_to_tsquery(figure)))
        .limit(top_n_figure)
    )
    if bbox:
        sel_figure = sel_figure.where(  # type: ignore
            func.ST_Intersects(osm_table.c.geom, _viewport_to_sql_bbox(bbox))
        )
    if isinstance(relation, InSpRelation):
        sel_ground = sel_figure.where(func.ST_GeometryType(osm_table.c.geom) == "ST_Point")
    cte_figure = sel_figure.cte("figure")

    sel_ground = (
        select([osm_table.c.geom])
        .where(osm_table.c.fts.op("@@")(func.websearch_to_tsquery(ground)))
        .limit(top_n_ground)
    )
    if bbox:
        sel_ground = sel_ground.where(  # type: ignore
            func.ST_Intersects(osm_table.c.geom, _viewport_to_sql_bbox(bbox))
        )
    if isinstance(relation, InSpRelation):
        sel_ground = sel_ground.where(func.ST_GeometryType(osm_table.c.geom) == "ST_Polygon")

    cte_ground = sel_ground.cte("ground")

    shape_cte = (
        select([cte_figure.c.geom, cte_figure.c.tags])
        .select_from(cte_figure.join(cte_ground, relation(cte_figure.c.geom, cte_ground.c.geom)))
        .limit(limit)  # type: ignore
        .offset(offset)
    ).cte("shapes")

    agg_cte = select(
        [
            func.jsonb_agg(_to_geojson(shape_cte.c.geom, shape_cte.c.tags)).label("features"),
            func.ST_Extent(shape_cte.c.geom).label("bbox"),
        ]
    ).cte("agg")

    stmt = select(
        [
            func.jsonb_build_object(
                "type",
                "FeatureCollection",
                "features",
                agg_cte.c.features,
                "bbox",
                agg_cte.c.bbox,
            ).label("features")
        ]
    )
    return stmt


async def run_spatial_relation(
    conn: AsyncConnection,
    *,
    figure: str,
    ground: str,
    relation: SpatialRelation,
    limit: Optional[int] = 20,
    top_n_figure: Optional[int] = 10,
    top_n_ground: Optional[int] = 10,
    bbox: Optional[ViewportBounds] = None,
    offset: Optional[int] = 0,
) -> Dict[str, Any]:
    """Fetch results for an ORM search."""
    stmt = create_query(
        figure=figure,
        ground=ground,
        relation=relation,
        limit=limit,
        top_n_figure=top_n_figure,
        top_n_ground=top_n_ground,
        bbox=bbox,
        offset=offset,
    )
    logger.error(stmt)
    results = await conn.execute(stmt)
    return results.fetchall()  # .first()
