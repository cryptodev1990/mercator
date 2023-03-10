"""Add stripe whitelist

Revision ID: 5e277ffd0dd3
Revises: 031edb6348bd
Create Date: 2022-11-02 00:40:49.628572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e277ffd0dd3'
down_revision = '031edb6348bd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('organizations', sa.Column('subscription_whitelist', sa.Boolean(), nullable=False, server_default=sa.text("FALSE")))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('organizations', 'subscription_whitelist')
    # ### end Alembic commands ###
