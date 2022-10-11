"""Add namespaces

Revision ID: 22480225f0bb
Revises: 41877eca4e70
Create Date: 2022-10-06 20:19:43.552811

"""
from alembic import op
import sqlalchemy as sa
from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_policy import PGPolicy
from alembic_utils.pg_trigger import PGTrigger
from sqlalchemy import text as sql_text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "22480225f0bb"
down_revision = "22c3030021c3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "namespaces",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False, comment="Namespace name"),
        sa.Column(
            "name_normalized",
            sa.String(),
            nullable=False,
            comment="Normalized namespace name. This is preprocessed prior to being inserted.\n                Uniqueness of names is determined by this and not by `name`.",
        ),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "properties",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::JSONB"),
            nullable=False,
            comment="Dict of properties used in the frontend, e.g. color.",
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_by_user_id",
            sa.Integer(),
            nullable=True,
            comment="ID of the user which created the namespace",
        ),
        sa.Column(
            "is_default",
            sa.Boolean(),
            sa.Computed(
                "name_normalized = 'default'",
            ),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["created_by_user_id"],
            ["users.id"],
            name=op.f("fk_namespaces_created_by_user_id"),
            deferrable=True,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_namespaces_organization_id"),
            deferrable=True,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_namespaces")),
        comment="A Namespace is a collection of shapes.\n\n    - Each shape is in one namespace.\n    - All organizations should have a 'Default' namespace.\n    ",
    )
    op.create_index(
        op.f("ix_namespaces_created_by_user_id"),
        "namespaces",
        ["created_by_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_namespaces_name_normalized"),
        "namespaces",
        ["name_normalized"],
        unique=False,
    )
    op.create_index(
        op.f("ix_namespaces_organization_id"),
        "namespaces",
        ["organization_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_unique_organization_name"),
        "namespaces",
        ["organization_id", "name_normalized"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.add_column(
        "shapes",
        sa.Column(
            "namespace_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            comment="If NULL, then in the default namespace",
        ),
    )
    op.create_index(
        op.f("ix_shapes_namespace_id"), "shapes", ["namespace_id"], unique=False
    )
    op.create_foreign_key(
        op.f("fk_shapes_namespace_id"),
        "shapes",
        "namespaces",
        ["namespace_id"],
        ["id"],
        deferrable=True,
    )
    public_create_default_namespace = PGFunction(
        schema="public",
        signature="create_default_namespace()",
        definition="returns trigger\n    LANGUAGE plpgsql\n    AS $function$\n        DECLARE\n            new_organization_id UUID;\n        BEGIN\n            INSERT INTO namespaces (name, name_normalized, organization_id)\n            VALUES\n            ('Default', 'default', NEW.id);\n\n            RETURN NEW;\n        END;\n    $function$",
    )
    op.create_entity(public_create_default_namespace)
    public_organizations_organizations_insert_trigger = PGTrigger(
        schema="public",
        signature="organizations_insert_trigger",
        on_entity="public.organizations",
        is_constraint=False,
        definition="AFTER INSERT ON public.organizations\n        FOR EACH ROW\n        EXECUTE FUNCTION create_default_namespace()",
    )
    op.create_entity(public_organizations_organizations_insert_trigger)

    conn = op.get_bind()
    conn.execute("GRANT ALL ON TABLE namespaces TO app_user;")
    public_namespaces_same_org = PGPolicy(
        schema="public",
        signature="same_org",
        on_entity="public.namespaces",
        definition="AS PERMISSIVE\nFOR ALL\nTO app_user\nUSING (app_user_org() = organization_id)\nWITH CHECK (app_user_org() = organization_id)",
    )
    op.create_entity(public_namespaces_same_org)


def downgrade() -> None:
    public_organizations_organizations_insert_trigger = PGTrigger(
        schema="public",
        signature="organizations_insert_trigger",
        on_entity="public.organizations",
        is_constraint=False,
        definition="AFTER UPDATE ON public.organizations\n        FOR EACH ROW\n        EXECUTE FUNCTION create_default_namespace()",
    )
    op.drop_entity(public_organizations_organizations_insert_trigger)

    public_create_default_namespace = PGFunction(
        schema="public",
        signature="create_default_namespace()",
        definition="returns trigger\n    LANGUAGE plpgsql\n    AS $function$\n        DECLARE\n            new_organization_id UUID;\n        BEGIN\n            INSERT INTO namespaces (name, name_normalized, organization_id)\n            VALUES\n            ('Default', 'default', NEW.id);\n\n            RETURN NEW;\n        END;\n    $function$",
    )
    op.drop_entity(public_create_default_namespace)
    public_namespaces_same_org = PGPolicy(
        schema="public",
        signature="same_org",
        on_entity="public.namespaces",
        definition="AS PERMISSIVE\nFOR ALL\nTO app_user\nUSING (app_user_org() = organization_id)\nWITH CHECK (app_user_org() = organization_id)",
    )
    op.drop_entity(public_namespaces_same_org)
    op.drop_constraint(op.f("fk_shapes_namespace_id"), "shapes", type_="foreignkey")
    op.drop_index(op.f("ix_shapes_namespace_id"), table_name="shapes")
    op.drop_column("shapes", "namespace_id")
    op.drop_index(
        "organization_id",
        table_name="namespaces",
        postgresql_where=sa.text("deleted_at IS NOT NULL"),
    )
    op.drop_index(op.f("ix_namespaces_organization_id"), table_name="namespaces")
    op.drop_index(op.f("ix_namespaces_name_normalized"), table_name="namespaces")
    op.drop_index(op.f("ix_namespaces_created_by_user_id"), table_name="namespaces")
    op.drop_table("namespaces")
