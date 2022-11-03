"""Add stripe subscription status to database

Revision ID: 35b59fb1b819
Revises: e8a93c0b7172
Create Date: 2022-11-02 15:40:06.030340

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35b59fb1b819'
down_revision = 'e8a93c0b7172'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('organizations', sa.Column('stripe_subscription_status', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('organizations', 'stripe_subscription_status')
