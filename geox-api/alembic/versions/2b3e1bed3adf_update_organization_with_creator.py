"""Update organization with creator

Revision ID: 2b3e1bed3adf
Revises: f7cbc2d71841
Create Date: 2022-08-08 22:33:58.624708

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2b3e1bed3adf'
down_revision = 'f7cbc2d71841'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organization_members', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('organizations', sa.Column('created_by_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'organizations', 'users', ['created_by_user_id'], ['id'], ondelete='SET NULL')
    op.add_column('shapes', sa.Column('organization_id', postgresql.UUID(), nullable=True))
    op.create_foreign_key(None, 'shapes', 'organizations', ['organization_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shapes', type_='foreignkey')
    op.drop_column('shapes', 'organization_id')
    op.drop_constraint(None, 'organizations', type_='foreignkey')
    op.drop_column('organizations', 'created_by_user_id')
    op.drop_column('organization_members', 'deleted_at')
    # ### end Alembic commands ###