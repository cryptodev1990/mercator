/**
 * Called by authorized_tile_function.py as part of running a custom tile function in TiMVT
 * Dev note: On hot-reloading for FastAPI, you'll have to restart the server to see changes to this file
 */

CREATE OR REPLACE FUNCTION generate_shape_tile(
    z INTEGER,
    x INTEGER,
    y INTEGER,
    filter_organization_id UUID,
    namespace_ids UUID[]
)
RETURNS bytea
AS $$
DECLARE
    result bytea;
BEGIN
    WITH
    bounds AS (
      SELECT ST_TileEnvelope(z, x, y) AS geom
    )
    , mvtgeom AS (
      SELECT ST_AsMVTGeom(ST_Transform(sh.geom, 3857), bounds.geom) AS geom
      , sh.properties - '__uuid' AS properties
      , sh.uuid AS "__uuid"
      , sh.namespace_id AS "__namespace_id"
      FROM public.shapes sh, bounds
      WHERE 1=1
        AND sh.organization_id = filter_organization_id
        AND sh.deleted_at IS NULL
        AND ST_Intersects(sh.geom, ST_Transform(bounds.geom, 4326))
	-- If the namespace parameter is empty, get all data
	AND COALESCE(namespace_id = ANY(namespace_ids), TRUE)
    )
    SELECT ST_AsMVT(mvtgeom.*)::bytea
    INTO result
    FROM mvtgeom
    ;

    RETURN result
    ;
END;
$$
LANGUAGE 'plpgsql'
STABLE
PARALLEL SAFE
;
