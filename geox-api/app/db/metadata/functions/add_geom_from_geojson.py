from alembic_utils.pg_function import PGFunction
from textwrap import dedent

add_geom_from_geojson = PGFunction(
    schema="public",
    signature="add_geom_from_geojson()",
    definition="""
    RETURNS trigger
    LANGUAGE plpgsql
    AS $function$
        BEGIN
            UPDATE shapes
            SET
                geom = ST_GeomFromGeoJson(geojson['geometry'])
                , properties = geojson['properties']
            WHERE 1=1
                AND uuid = NEW.uuid
            ;
            RETURN NEW;
        END;
    $function$
    """
)
