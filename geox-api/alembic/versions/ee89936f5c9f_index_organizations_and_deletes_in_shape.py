"""Index organizations and deletes in shape

Revision ID: ee89936f5c9f
Revises: ee5e297dda1d
Create Date: 2022-09-17 16:39:50.991807

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ee89936f5c9f'
down_revision = 'ee5e297dda1d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f('ix_shapes_deleted_at'), 'shapes', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_shapes_organization_id'), 'shapes', ['organization_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_shapes_organization_id'), table_name='shapes')
    op.drop_index(op.f('ix_shapes_deleted_at'), table_name='shapes')
