"""Updates to GeoJSON update properties and geoms

Revision ID: 3a5e81cddc7e
Revises: 5955e3fda040
Create Date: 2022-09-30 23:49:24.241224

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a5e81cddc7e'
down_revision = '952810c021bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
        BEGIN;
          CREATE FUNCTION update_geom_from_geojson()
          RETURNS TRIGGER AS
          $_$
          BEGIN
             UPDATE shapes
             SET geom = ST_GeomFromGeoJson(geojson['geometry'])
             , properties = geojson['properties']
             WHERE 1=1
               AND uuid = NEW.uuid
             ;
             RETURN NEW;
          END;
          $_$
          LANGUAGE 'plpgsql';

          CREATE TRIGGER shapes_update_geom_trigger
          AFTER UPDATE on "shapes"
            FOR EACH ROW
            WHEN (pg_trigger_depth() = 0)
            EXECUTE PROCEDURE update_geom_from_geojson();
        END;
    """)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute("""
        BEGIN;
          DROP TRIGGER shapes_update_geom_trigger ON shapes;
          DROP FUNCTION update_geom_from_geojson;
        END;
    """)

