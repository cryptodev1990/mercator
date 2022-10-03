"""Remove db-credentials.

Revision ID: a785ddebaee8
Revises: c2667d46ff0f
Create Date: 2022-08-30 13:25:43.225416

Namespaces are a future feature that aren't currently being used.
This will simplify the values.

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "a785ddebaee8"
down_revision = "c2667d46ff0f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_db_credentials_name", table_name=op.f("db_credentials"))
    op.drop_table("db_credentials")


def downgrade() -> None:
    op.create_table(
        "db_credentials",
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "id",
            postgresql.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "organization_id", postgresql.UUID(), autoincrement=False, nullable=True
        ),
        sa.Column("is_default", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column(
            "created_by_user_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "updated_by_user_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column("db_driver", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("db_user", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("db_password", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("db_host", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("db_port", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("db_database", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("db_extras", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("db_credentials_created_by_user_id_fkey"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("db_credentials_organization_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_user_id"],
            ["users.id"],
            name=op.f("db_credentials_updated_by_user_id_fkey"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("db_credentials_pkey")),
    )
    op.create_index("ix_db_credentials_name", "db_credentials", ["name"], unique=False)
