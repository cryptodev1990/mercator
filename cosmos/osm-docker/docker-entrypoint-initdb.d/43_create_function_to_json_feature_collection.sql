CREATE OR REPLACE FUNCTION _geojson_feature_collection_agg_sfunc(prev JSONB, g GEOMETRY, properties JSONB DEFAULT '{}'::JSONB, id TEXT DEFAULT NULL)
RETURNS JSONB
CALLED ON NULL INPUT
STABLE
LANGUAGE PLPGSQL
AS
$$
DECLARE
    xmin NUMERIC;
    xmax NUMERIC;
    ymin NUMERIC;
    ymax NUMERIC;
    feature JSONB;
BEGIN
    IF g is NULL
        THEN RETURN prev;
    END IF;
    xmin := least(cast(prev #> '{bbox,0}' AS NUMERIC), ST_XMin(g));
    ymin := least(cast(prev #> '{bbox,1}' as NUMERIC), ST_YMin(g));
    xmax := greatest(cast(prev #> '{bbox,2}' as NUMERIC), ST_XMax(g));
    ymax := greatest(cast(prev #> '{bbox,3}' as NUMERIC), ST_YMax(g));
    feature := to_geojson_feature(g, properties=>properties, id=>id);
    RETURN jsonb_build_object(
        'type', 'FeatureCollection',
        'features', coalesce(prev->'features', jsonb_build_array()) || feature,
        'bbox', json_build_array(xmin, ymin, xmax, ymax)
    );
END
$$;

CREATE OR REPLACE FUNCTION _geojson_feature_collection_agg_sfunc(prev JSONB, g GEOMETRY)
RETURNS JSONB
CALLED ON NULL INPUT
STABLE
LANGUAGE SQL
AS
$$
SELECT _geojson_feature_collection_sfunc(prev, g, '{}'::JSONB);
$$;

CREATE OR REPLACE FUNCTION _geojson_feature_collection_agg_combine(a JSONB, b JSONB)
RETURNS JSONB
CALLED ON NULL INPUT
STABLE
LANGUAGE SQL
AS
$$
SELECT
    CASE
    WHEN a is NULL THEN b
    WHEN b is NULL THEN a
    ELSE jsonb_build_object(
        'type', 'FeatureCollection',
        'features', coalesce(a->'features', jsonb_build_array()) || coalesce(b->'features', jsonb_build_array()),
        'bbox',
        json_build_array(
            least((a #> '{bbox,0}')::NUMERIC, (b #> '{bbox,0}')::NUMERIC),
            least((a #> '{bbox,1}')::NUMERIC, (b #> '{bbox,1}')::NUMERIC),
            greatest((a #> '{bbox,2}')::NUMERIC, (b #> '{bbox,2}')::NUMERIC),
            greatest((a #> '{bbox,3}')::NUMERIC, (b #> '{bbox,3}')::NUMERIC)
        )
    )
    END;
$$;

CREATE OR REPLACE AGGREGATE to_geojson_feature_collection_agg(g GEOMETRY, properties JSONB, id TEXT) (
    SFUNC = _geojson_feature_collection_agg_sfunc,
    STYPE = JSONB,
    COMBINEFUNC = _geojson_feature_collection_agg_combine,
    INITCOND = '{"type": "FeatureCollection", "features": []}'
);
-- Accepts a set of GEOMETRY values and properties and returns a GeoJSON FeatureCollection.

CREATE OR REPLACE AGGREGATE to_geojson_feature_collection_agg(g GEOMETRY) (
    SFUNC = _geojson_feature_collection_agg_sfunc,
    STYPE = JSONB,
    COMBINEFUNC = _geojson_feature_collection_agg_combine,
    INITCOND = '{"type": "FeatureCollection", "features": []}'
);
-- Accepts a set of GEOMETRY values and returns a GeoJSON FeatureCollection.