"""Add shapes

Revision ID: 77e1dfc7dc02
Revises: f82aca05f460
Create Date: 2022-09-15 18:17:09.970522

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '77e1dfc7dc02'
down_revision = 'f82aca05f460'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute("ALTER TABLE shapes ADD COLUMN geom GEOMETRY")
    conn.execute("UPDATE shapes SET geom = ST_GeomFromGeoJSON(geojson['geometry'])")
    conn.execute("CREATE INDEX idx_shapes_geom ON shapes USING GIST(geom)")


def downgrade() -> None:
    op.drop_index("idx_shapes_geom", table_name="shapes", postgresql_using="gist")
    op.drop_column("shapes", "geom")
