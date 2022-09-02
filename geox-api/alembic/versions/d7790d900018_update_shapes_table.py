"""Update shapes table

Revision ID: d7790d900018
Revises: 6cf78a62d412
Create Date: 2022-09-01 21:20:33.943197

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd7790d900018'
down_revision = '6cf78a62d412'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint('shapes_deleted_at_by_user_id_fkey', 'shapes', type_='foreignkey')
    op.alter_column('shapes', "deleted_at_by_user_id",  new_column_name="deleted_by_user_id")
    op.create_foreign_key("shapes_deleted_by_user_id", 'shapes', 'users', ['deleted_by_user_id'], ['id'])
    op.alter_column('shapes', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=sa.func.now(),
               nullable=False)
    op.alter_column('shapes', 'created_by_user_id',
               existing_type=sa.INTEGER(),
               server_default=None,
               nullable=False)
    op.alter_column('shapes', 'geojson',
               existing_type=postgresql.JSON(astext_type=sa.Text()),
               type_=postgresql.JSONB(astext_type=sa.Text()),
               existing_nullable=False)
    op.alter_column('shapes', 'organization_id',
               existing_type=postgresql.UUID(),
               nullable=False)


def downgrade() -> None:
    op.drop_constraint('shapes_deleted_by_user_id_fkey', 'shapes', type_='foreignkey')
    op.alter_column('shapes', "deleted_by_user_id",  new_column_name="deleted_at_by_user_id")
    op.create_foreign_key('shapes_deleted_at_by_user_id_fkey', 'shapes', 'users', ['deleted_at_by_user_id'], ['id'])
    op.alter_column('shapes', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               server_default=None,
               nullable=True)
    op.alter_column('shapes', 'created_by_user_id',
               existing_type=sa.INTEGER(),
               server_default=None,
               nullable=True)
    op.alter_column('shapes', 'organization_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    op.alter_column('shapes', 'geojson',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=postgresql.JSON(astext_type=sa.Text()),
               existing_nullable=False)
    op.create_foreign_key(None, 'shapes', 'users', ['deleted_by_user_id'], ['id'])
    op.create_foreign_key(None, 'shapes', 'users', ['deleted_by_user_id'], ['id'])

