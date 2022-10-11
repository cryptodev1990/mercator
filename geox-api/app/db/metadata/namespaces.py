"""Namespaces Table"""
from cProfile import label
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

# Alternative implementation: Should NULL namespace be an implicit 'default' namespace?
# probably not. We'd display it as default - and we'd need to disallow

namespaces = Table(
    "namespaces",
    metadata,
    *UUIDMixin(),
    # CIText used in order to make name uniqueness case-insensitive
    Column("name", String(), nullable=False, comment="Namespace name"),
    Column(
        "name_normalized",
        String(),
        nullable=False,
        comment=dedent(
            """
                Normalized namespace name. This is preprocessed prior to being inserted.
                Uniqueness of names is determined by this and not by `name`.""".strip()
        ),
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
        default=dict(),
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
    Column("is_default", Boolean(), Computed("name_normalized = 'Default'")),
    # This partial index ensures that the name is unique within an organization - only considering active organizations,
    Index(
        "ix_unique_organization_name",
        "organization_id",
        "name_normalized",
        unique=True,
        postgresql_where=text("deleted_at IS  NULL"),
    ),
    comment="""A Namespace is a collection of shapes.

    - Each shape is in one namespace.
    - All organizations should have a 'Default' namespace.
    """,
)
