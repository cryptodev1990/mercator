"""Add trigger to create geometry from geojson

Revision ID: 29413b133313
Revises: ee89936f5c9f
Create Date: 2022-09-18 05:17:11.228452

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '29413b133313'
down_revision = 'ee89936f5c9f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
        CREATE FUNCTION add_geom_from_geojson()
          RETURNS trigger AS
          $_$
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
        $_$
        LANGUAGE 'plpgsql';

        CREATE TRIGGER shapes_create_geom_trigger
          AFTER INSERT ON "shapes"
            FOR EACH ROW
            EXECUTE PROCEDURE add_geom_from_geojson();
    """)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
        DROP TRIGGER shapes_create_geom_trigger ON shapes;
        DROP FUNCTION add_geom_from_geojson;
    """)
