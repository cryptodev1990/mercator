"""Add searchable metadata for shapes

Revision ID: a7c6886c3610
Revises: e4994335c3e0
Create Date: 2022-09-25 17:47:13.175350

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app import models

# revision identifiers, used by Alembic.
revision = 'a7c6886c3610'
down_revision = 'e4994335c3e0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('shapes', sa.Column(
        'fts', models.shape.TSVector(), sa.Computed("to_tsvector('english', properties - '__uuid')", persisted=True), nullable=True))
    op.create_index('ix_properties_fts', 'shapes', [
                    'fts'], unique=False, postgresql_using='gin')
    conn = op.get_bind()
    conn.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade() -> None:
    op.drop_index('ix_properties_fts',
                  table_name='shapes', postgresql_using='gin')
    op.drop_column('shapes', 'fts')
    conn = op.get_bind()
    conn.execute("DROP EXTENSION pg_trgm;")
