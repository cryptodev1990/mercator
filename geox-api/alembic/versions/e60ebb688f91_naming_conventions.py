"""Naming conventions

Revision ID: e60ebb688f91
Revises: 952810c021bd
Create Date: 2022-10-02 22:07:32.985087

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e60ebb688f91'
down_revision = '952810c021bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(op.f('organization_members_user_id_organization_id_key'), 'organization_members', type_='unique')
    op.create_unique_constraint(op.f('uq_organization_members_user_id'), 'organization_members', ['user_id', 'organization_id'])


def downgrade() -> None:
    op.drop_constraint(op.f('uq_organization_members_user_id'), 'organization_members', type_='unique')
    op.create_unique_constraint(op.f('organization_members_user_id_organization_id_key'), 'organization_members', ['user_id', 'organization_id'])
