CREATE OR REPLACE FUNCTION to_geojson_feature(
    g GEOMETRY,
    properties JSONB DEFAULT '{}'::JSONB,
    id TEXT DEFAULT NULL
)
RETURNS JSONB
CALLED ON NULL INPUT
STABLE
PARALLEL SAFE
LANGUAGE SQL
AS
$$
SELECT
    CASE
    WHEN g is NULL THEN NULL
    ELSE json_build_object(
                    'type', 'Feature',
                    'geometry', ST_AsGeoJSON(g)::JSONB,
                    'properties', coalesce(properties, jsonb_build_object()),
                    'id', id,
                    'bbox', jsonb_build_array(ST_XMin(g), ST_YMin(g), ST_XMax(g), ST_YMax(g))
        )
    END;
$$
--  GEOMETRY values and returns a GeoJSON FeatureCollection.
