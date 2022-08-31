"""Add app_org function

Revision ID: 1c5fdf8ce69c
Revises: 7f6fb9c3c570
Create Date: 2022-08-26 17:58:10.899395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c5fdf8ce69c'
down_revision = '7f6fb9c3c570'
branch_labels = None
depends_on = None

def create_function_app_user_org(conn: sa.engine.Connection) -> None:
    conn.execute(
        sa.text("""
        CREATE FUNCTION app_user_org()
        RETURNS UUID
        AS
        $$
        SELECT organization_id
        FROM organization_members
        WHERE deleted_at IS NULL
            AND active
            AND user_id = app_user_id()
        $$
        LANGUAGE SQL
        SECURITY DEFINER;
        """)
    )

def drop_function_app_user_org(conn: sa.engine.Connection) -> None:
    conn.execute(sa.text("""
    DROP FUNCTION app_user_org;
    """))

def upgrade() -> None:
    conn = op.get_bind()
    create_function_app_user_org(conn)

def downgrade() -> None:
    conn = op.get_bind()
    drop_function_app_user_org(conn)
