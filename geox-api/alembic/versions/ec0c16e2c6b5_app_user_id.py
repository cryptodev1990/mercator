"""Add UDF app_user_id()

Revision ID: ec0c16e2c6b5
Revises: a6d124f8653c
Create Date: 2022-08-16 14:29:14.398802

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec0c16e2c6b5'
down_revision = 'a6d124f8653c'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    conn = op.get_bind()
    statement ="""
        CREATE FUNCTION app_user_id()
        RETURNS INTEGER
        AS $$
        SELECT nullif(current_setting('app.user_id', TRUE), '')::INTEGER
        $$
        LANGUAGE SQL
        SECURITY DEFINER;
    """
    conn.execute(statement)

def downgrade() -> None:
    conn = op.get_bind()
    statement = """DROP FUNCTION app_user_id();"""
    conn.execute(statement)
