"""Shape model."""
import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Computed  # type: ignore
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    Table,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID

from app.db.metadata.common import metadata

__all__ = ["shapes"]


shapes = Table(
    "shapes",
    metadata,
    Column(
        "uuid",
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    ),
    Column("name", String, index=True),
    Column(
        "created_at",
        DateTime,
        default=datetime.datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    ),
    Column(
        "created_by_user_id",
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        server_default=func.app_user_id(),
    ),
    Column(
        "updated_at",
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
        server_default=func.now(),
    ),
    Column(
        "updated_by_user_id",
        Integer,
        ForeignKey("users.id"),
        server_default=func.app_user_id(),
        nullable=False,
    ),
    Column("deleted_at", DateTime, nullable=True, index=True),
    Column("deleted_by_user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("geom", Geometry(srid=4326), nullable=True),
    Column(
        "properties",
        JSONB,
        nullable=False,
        default=dict,
        server_default="json_build_object()",
    ),
    Column(
        "organization_id",
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        server_default=func.app_user_org(),
        index=True,
        nullable=False,
    ),
    Column(
        "fts",
        TSVECTOR(),
        Computed("to_tsvector('english', properties)", persisted=True),
    ),
    # This is unlikely - actualy behavior - at the app level is to delete the shape when the org is soft-deleted
    Index("ix_properties_fts", "fts", postgresql_using="gin"),
    Column(
        "namespace_id",
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    ),
    # The shape namespace must both exist and be in the same organization as the shape
    ForeignKeyConstraint(
        ["namespace_id", "organization_id"],
        ["namespaces.id", "namespaces.organization_id"],
    ),
)
