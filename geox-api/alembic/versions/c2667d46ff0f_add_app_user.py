"""Add app user.

Revision ID: c2667d46ff0f
Revises: ec0c16e2c6b5
Create Date: 2022-08-19 19:26:25.296392

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2667d46ff0f'
down_revision = 'ec0c16e2c6b5'
branch_labels = None
depends_on = None


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP ROLE IF EXISTS app_user"))


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DROP ROLE IF EXISTS app_user"))
    conn.execute(sa.text("CREATE ROLE app_user"))
    conn.execute(sa.text("GRANT ALL ON ALL TABLES IN SCHEMA public TO app_user"))
