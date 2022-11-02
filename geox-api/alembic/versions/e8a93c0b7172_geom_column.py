"""Geom column

Revision ID: e8a93c0b7172
Revises: 66305926d854
Create Date: 2022-10-27 17:04:14.128367

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
from sqlalchemy import text as sql_text
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import text as sql_text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e8a93c0b7172"
down_revision = "66305926d854"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    public_shapes_shapes_create_geom_trigger = PGTrigger(
        schema="public",
        signature="shapes_create_geom_trigger",
        on_entity="public.shapes",
        is_constraint=False,
        definition="AFTER INSERT ON public.shapes FOR EACH ROW EXECUTE FUNCTION add_geom_from_geojson()",
    )
    op.drop_entity(public_shapes_shapes_create_geom_trigger)

    public_shapes_shapes_update_geom_trigger = PGTrigger(
        schema="public",
        signature="shapes_update_geom_trigger",
        on_entity="public.shapes",
        is_constraint=False,
        definition="AFTER UPDATE ON public.shapes FOR EACH ROW WHEN ((pg_trigger_depth() = 0)) EXECUTE FUNCTION update_geom_from_geojson()",
    )
    op.drop_entity(public_shapes_shapes_update_geom_trigger)

    public_update_geom_from_geojson = PGFunction(
        schema="public",
        signature="update_geom_from_geojson()",
        definition="returns trigger\n LANGUAGE plpgsql\nAS $function$\nBEGIN\n    UPDATE shapes\n    SET geom = ST_GeomFromGeoJson(geojson['geometry'])\n    , properties = geojson['properties']\n    , name = geojson #>> '{properties,name}'\n    WHERE 1=1\n    AND uuid = NEW.uuid\n    ;\n    RETURN NEW;\nEND;\n$function$",
    )
    op.drop_entity(public_update_geom_from_geojson)

    public_add_geom_from_geojson = PGFunction(
        schema="public",
        signature="add_geom_from_geojson()",
        definition="returns trigger\n LANGUAGE plpgsql\nAS $function$\n        BEGIN\n            UPDATE shapes\n            SET\n                geom = ST_GeomFromGeoJson(geojson['geometry'])\n                , properties = geojson['properties']\n                , name = geojson #>> '{properties,name}'\n            WHERE 1=1\n                AND uuid = NEW.uuid\n            ;\n            RETURN NEW;\n        END;\n    $function$",
    )
    op.drop_entity(public_add_geom_from_geojson)

    public_shape_geojson = PGFunction(
        schema="public",
        signature="shape_geojson(uuid UUID, geom GEOMETRY, properties JSONB, name TEXT)",
        definition="RETURNS JSONB\nLANGUAGE SQL\nSTABLE\nAS\n$function$\n    SELECT jsonb_build_object(\n        'geometry',\n        ST_AsGeoJSON(geom),\n        'properties',\n        properties || jsonb_build_object('name', name, '__uuid', uuid :: TEXT),\n        'id',\n        to_jsonb(uuid :: TEXT),\n        'bbox',\n        jsonb_build_array(ST_xmin(geom), ST_ymin(geom), ST_xmax(geom), ST_ymax(geom))\n    )\n$function$",
    )
    op.create_entity(public_shape_geojson)

    conn.execute(
        "ALTER TABLE shapes ALTER COLUMN properties SET default '{}'::JSONB, ALTER COLUMN properties SET NOT NULL"
    )
    op.drop_column("shapes", "geojson")


def downgrade() -> None:
    conn = op.get_bind()
    op.add_column(
        "shapes",
        sa.Column(
            "geojson",
            postgresql.JSONB,
            autoincrement=False,
            nullable=True,
        ),
    )
    conn.execute("UPDATE SET geojson = shape_geojson(uuid, geom, properties, name)")
    op.alter_column("shapes", "geojson", nullable=False)
    op.alter_column("shapes", "properties", nullable=True)

    public_shape_geojson = PGFunction(
        schema="public",
        signature="shape_geojson(uuid UUID, geom GEOMETRY, properties JSONB, name TEXT)",
        definition="RETURNS JSONB\nLANGUAGE SQL\nSTABLE\nAS\n$function$\n    SELECT jsonb_build_object(\n        'geometry',\n        ST_AsGeoJSON(geom),\n        'properties',\n        properties || jsonb_build_object('name', name, '__uuid', uuid :: TEXT),\n        'id',\n        to_jsonb(uuid :: TEXT),\n        'bbox',\n        jsonb_build_array(ST_xmin(geom), ST_ymin(geom), ST_xmax(geom), ST_ymax(geom))\n    )\n$function$",
    )
    op.drop_entity(public_shape_geojson)

    public_add_geom_from_geojson = PGFunction(
        schema="public",
        signature="add_geom_from_geojson()",
        definition="returns trigger\n LANGUAGE plpgsql\nAS $function$\n        BEGIN\n            UPDATE shapes\n            SET\n                geom = ST_GeomFromGeoJson(geojson['geometry'])\n                , properties = geojson['properties']\n                , name = geojson #>> '{properties,name}'\n            WHERE 1=1\n                AND uuid = NEW.uuid\n            ;\n            RETURN NEW;\n        END;\n    $function$",
    )
    op.create_entity(public_add_geom_from_geojson)

    public_update_geom_from_geojson = PGFunction(
        schema="public",
        signature="update_geom_from_geojson()",
        definition="returns trigger\n LANGUAGE plpgsql\nAS $function$\nBEGIN\n    UPDATE shapes\n    SET geom = ST_GeomFromGeoJson(geojson['geometry'])\n    , properties = geojson['properties']\n    , name = geojson #>> '{properties,name}'\n    WHERE 1=1\n    AND uuid = NEW.uuid\n    ;\n    RETURN NEW;\nEND;\n$function$",
    )
    op.create_entity(public_update_geom_from_geojson)

    public_shapes_shapes_update_geom_trigger = PGTrigger(
        schema="public",
        signature="shapes_update_geom_trigger",
        on_entity="public.shapes",
        is_constraint=False,
        definition="AFTER UPDATE ON public.shapes FOR EACH ROW WHEN ((pg_trigger_depth() = 0)) EXECUTE FUNCTION update_geom_from_geojson()",
    )
    op.create_entity(public_shapes_shapes_update_geom_trigger)

    public_shapes_shapes_create_geom_trigger = PGTrigger(
        schema="public",
        signature="shapes_create_geom_trigger",
        on_entity="public.shapes",
        is_constraint=False,
        definition="AFTER INSERT ON public.shapes FOR EACH ROW EXECUTE FUNCTION add_geom_from_geojson()",
    )
    op.create_entity(public_shapes_shapes_create_geom_trigger)
