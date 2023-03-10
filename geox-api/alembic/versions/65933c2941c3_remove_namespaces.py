"""Remove namespaces table

Revision ID: 65933c2941c3
Revises: a785ddebaee8
Create Date: 2022-08-30 14:02:50.279850

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "65933c2941c3"
down_revision = "a785ddebaee8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_namespaces_id", table_name=op.f("namespaces"))
    op.drop_index(
        "ix_namespace_members_added_by_user_id", table_name=op.f("namespace_members")
    )
    op.drop_index("ix_namespace_members_id", table_name=op.f("namespace_members"))
    op.drop_index("ix_namespace_members_namespace_id", table_name=op.f("namespace_members"))
    op.drop_index("ix_namespace_members_user_id", table_name=op.f("namespace_members"))
    op.drop_table("namespace_members")
    op.drop_constraint(op.f("shapes_namespace_id_fkey"), "shapes", type_="foreignkey")
    op.drop_column("shapes", "namespace_id")
    op.drop_table("namespaces")


def downgrade() -> None:
    op.create_table(
        "namespaces",
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "created_by_user_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "organization_id", postgresql.UUID(), autoincrement=False, nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("namespaces_created_by_user_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("namespaces_organization_id_fkey"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("namespaces_pkey")),
    )
    op.add_column(
        "shapes",
        sa.Column("namespace_id", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.create_table(
        "namespace_members",
        sa.Column(
            "created_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "updated_at", postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
        sa.Column("has_read", sa.BOOLEAN(), autoincrement=False, nullable=False, server_default=sa.text("TRUE")),
        sa.Column("has_write", sa.BOOLEAN(), autoincrement=False, nullable=False, server_default=sa.text("TRUE")),
        sa.Column("is_admin", sa.BOOLEAN(), autoincrement=False, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("namespace_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("added_by_user_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["added_by_user_id"],
            ["users.id"],
            name=op.f("namespace_members_added_by_user_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["namespace_id"],
            ["namespaces.id"],
            name=op.f("namespace_members_namespace_id_fkey"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("namespace_members_user_id_fkey")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("namespace_members_pkey")),
    )
    op.create_index("ix_namespaces_id", "namespaces", ["id"], unique=False)
    op.create_foreign_key(
        "shapes_namespace_id_fkey", "shapes", "namespaces", ["namespace_id"], ["id"]
    )

    op.create_index(
        "ix_namespace_members_user_id", "namespace_members", ["user_id"], unique=False
    )
    op.create_index(
        "ix_namespace_members_namespace_id",
        "namespace_members",
        ["namespace_id"],
        unique=False,
    )
    op.create_index(
        "ix_namespace_members_id", "namespace_members", ["id"], unique=False
    )
    op.create_index(
        "ix_namespace_members_added_by_user_id",
        "namespace_members",
        ["added_by_user_id"],
        unique=False,
    )