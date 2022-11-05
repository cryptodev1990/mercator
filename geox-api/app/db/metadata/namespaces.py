"""Namespaces Table"""
from textwrap import dedent

from sqlalchemy import (  # type: ignore
    Boolean,
    CheckConstraint,
    Column,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from .common import TimestampMixin, UUIDMixin, metadata

__all__ = ["namespaces"]

namespaces = Table(
    "namespaces",
    metadata,
    *UUIDMixin(),
    # CIText used in order to make name uniqueness case-insensitive
    Column("name", String(), nullable=False, comment="Namespace name"),
    Column(
        "slug",
        String(),
        nullable=False,
        comment=dedent(
            """
                Normalized namespace name. This is preprocessed prior to being inserted.
                Uniqueness of names is determined by this and not by `name`."""
        ).strip(),
        index=True,
    ),
    Column(
        "organization_id",
        UUID(as_uuid=True),
        ForeignKey("organizations.id", deferrable=True),
        nullable=False,
        index=True,
    ),
    Column(
        "properties",
        JSONB,
        nullable=False,
        comment="Dict of properties used in the frontend, e.g. color.",
        server_default=text("'{}'::JSONB"),
        default=dict,
    ),
    *TimestampMixin(),
    Column("deleted_at", DateTime, nullable=True),
    Column(
        "created_by_user_id",
        Integer(),
        ForeignKey("users.id", deferrable=True),
        nullable=True,
        index=True,
        comment="ID of the user which created the namespace",
    ),
    Column(
        "is_default",
        Boolean(),
        Computed("coalesce(slug = 'default', FALSE)"),
        nullable=False,
    ),
    # This partial index ensures that the name is unique within an organization - only considering active organizations,
    Index(
        "ix_unique_organization_slug",
        "organization_id",
        "slug",
        unique=True,
        postgresql_where=text("deleted_at IS NULL"),
    ),
    # this is duplicate, but needed for setting a foreign key in shapes
    Index(
        "ix_unique_id_organization_id",
        "id",
        "organization_id",
        unique=True,
    ),
    CheckConstraint("slug SIMILAR TO '[a-z0-9-_]+'", name="slug_is_valid"),
    comment=dedent(
        """A Namespace is a collection of shapes.

    - Each shape is in one namespace.
    - All organizations should have a 'Default' namespace.
    """
    ).strip(),
)

# Note: every organization should have one and only one default organization that is active
# however this cannot be easily put into constraints in the current schema.
# The convention that the default namespace is always named "Default" + unique slug constrains
# there to be only one active default namespace. A trigger creates the "default" namespace for
# each new organization. However, nothing prevents deleting the default namespace other than
# application code.
