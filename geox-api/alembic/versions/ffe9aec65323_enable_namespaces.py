"""Enable namespaces

Revision ID: ffe9aec65323
Revises: 22480225f0bb
Create Date: 2022-10-11 12:41:08.485286

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ffe9aec65323"
down_revision = "22480225f0bb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Create default namespaces for any organization missing one
    conn.execute(
        sa.text(
            """insert into namespaces (organization_id, name, name_normalized)
                select o.id AS organization_id, 'Default' as name, 'default' as name_normalized
                from organizations as o
                left join namespaces as n on n.organization_id = o.id
                    and n.is_default
                where n.id is null"""
        )
    )
    # Put existing shapes into the default namespace
    conn.execute(
        sa.text(
            """UPDATE shapes AS s
            SET namespace_id = n.id
            FROM namespaces AS n
            WHERE n.is_default and n.organization_id = s.organization_id
    """
        )
    )

    op.create_index(
        "ix_unique_id_organization_id",
        "namespaces",
        ["id", "organization_id"],
        unique=True,
    )
    op.alter_column(
        "shapes",
        "namespace_id",
        existing_type=postgresql.UUID(),
        nullable=False,
        comment=None,
        existing_comment="If NULL, then in the default namespace",
    )
    # Need to user raw SQL because op.drop_constraint doesn't work
    # for whatever reason - updating from master causes a problem without this,
    # while a blank database does not. This should work in either case.
    conn = op.get_bind()
    conn.execute(
        """
                  ALTER TABLE shapes DROP CONSTRAINT IF EXISTS fk_shapes_namespace_id;
                 """
    )

    # op.drop_constraint(op.f("fk_shapes_namespace_id"), "shapes", type_="foreignkey")
    op.create_foreign_key(
        op.f("fk_shapes_namespace_id"),
        "shapes",
        "namespaces",
        ["namespace_id", "organization_id"],
        ["id", "organization_id"],
    )


def downgrade() -> None:

    op.drop_constraint(op.f("fk_shapes_namespace_id"), "shapes", type_="foreignkey")
    op.alter_column(
        "shapes",
        "namespace_id",
        existing_type=postgresql.UUID(),
        nullable=True,
        comment="If NULL, then in the default namespace",
    )
    op.drop_index("ix_unique_id_organization_id", table_name="namespaces")
