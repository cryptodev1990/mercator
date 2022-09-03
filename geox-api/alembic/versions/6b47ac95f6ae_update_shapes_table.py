"""Update shapes table

Revision ID: 6b47ac95f6ae
Revises: d7790d900018
Create Date: 2022-09-02 16:58:17.884798

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b47ac95f6ae"
down_revision = "d7790d900018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "shapes", "created_by_user_id", server_default=sa.text("app_user_id()")
    )
    op.alter_column(
        "shapes",
        "updated_by_user_id",
        nullable=False,
        server_default=sa.text("app_user_id()"),
    )
    op.alter_column(
        "shapes", "created_by_user_id", server_default=sa.text("app_user_id()")
    )
    op.alter_column(
        "shapes",
        "organization_id",
        nullable=False,
        server_default=sa.text("app_user_org()"),
    )
    op.alter_column(
        "shapes", "updated_at", nullable=False, server_default=sa.text("now()")
    )
    op.alter_column("shapes", "created_at", server_default=sa.text("now()"))


def downgrade() -> None:
    op.alter_column("shapes", "created_by_user_id", server_default=None)
    op.alter_column("shapes", "updated_by_user_id", nullable=True, server_default=None)
    op.alter_column("shapes", "created_by_user_id", server_default=None)
    op.alter_column("shapes", "organization_id", nullable=True, server_default=None)
    op.alter_column("shapes", "updated_at", nullable=True, server_default=None)
    op.alter_column("shapes", "created_at", server_default=None)
