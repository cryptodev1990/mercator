"""Add updated_at column to shapes

Revision ID: e64231091dd2
Revises: 83b9345798d9
Create Date: 2022-07-07 15:45:49.070282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e64231091dd2'
down_revision = '83b9345798d9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shapes', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('shapes', sa.Column('updated_by_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'shapes', 'users', ['updated_by_user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shapes', type_='foreignkey')
    op.drop_column('shapes', 'updated_by_user_id')
    op.drop_column('shapes', 'updated_at')
    # ### end Alembic commands ###