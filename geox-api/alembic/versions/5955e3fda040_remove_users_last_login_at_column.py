"""Remove users last_login_at column

Revision ID: 5955e3fda040
Revises: a7c6886c3610
Create Date: 2022-09-28 10:27:27.204015

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5955e3fda040'
down_revision = 'e1aadd0537a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('users', 'last_login_at')


def downgrade() -> None:
    op.add_column('users', sa.Column('last_login_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
