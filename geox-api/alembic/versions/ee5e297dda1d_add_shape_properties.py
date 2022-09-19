"""Add shape properties

Revision ID: ee5e297dda1d
Revises: 77e1dfc7dc02
Create Date: 2022-09-16 18:26:54.844250

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ee5e297dda1d'
down_revision = '77e1dfc7dc02'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('shapes', sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    conn = op.get_bind()
    conn.execute("UPDATE shapes SET properties = (geojson->>0)::JSON->'properties' WHERE geojson->>0 IS NOT NULL")
    conn.execute("UPDATE shapes SET properties = geojson['properties'] WHERE geojson['properties'] IS NOT NULL")


def downgrade() -> None:
    op.drop_column('shapes', 'properties')
