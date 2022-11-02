from textwrap import dedent

from alembic_utils.pg_function import PGFunction

__all__ = ["shape_geojson_uuid_geometry_jsonb_text"]

shape_geojson_uuid_geometry_jsonb_text = PGFunction(
    schema="public",
    signature="shape_geojson(uuid UUID, geom GEOMETRY, properties JSONB, name TEXT)",
    definition=dedent(
        """
        RETURNS JSONB
        LANGUAGE SQL
        STABLE
        AS
        $function$
            SELECT jsonb_build_object(
                'geometry',
                ST_AsGeoJSON(geom),
                'properties',
                properties || jsonb_build_object('name', name, '__uuid', uuid :: TEXT),
                'id',
                to_jsonb(uuid :: TEXT),
                'bbox',
                jsonb_build_array(ST_xmin(geom), ST_ymin(geom), ST_xmax(geom), ST_ymax(geom))
            )
        $function$
        """
    ).strip(),
)
