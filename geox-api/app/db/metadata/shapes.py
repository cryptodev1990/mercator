"""Shape model."""
from geoalchemy2 import Geometry
from sqlalchemy import (  # type: ignore
    Column,
    Computed,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator

from app.db.metadata.common import metadata

__all__ = ["shapes"]


class TSVector(TypeDecorator):
    impl = TSVECTOR


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
        default=func.now(),
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
    Column("updated_at", DateTime, default=func.now(), server_default=func.now()),
    Column(
        "updated_by_user_id",
        Integer,
        ForeignKey("users.id"),
        server_default=func.app_user_id(),
        nullable=False,
    ),
    Column("deleted_at", DateTime, nullable=True, index=True),
    Column("deleted_by_user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("geojson", JSONB, nullable=False),
    Column("geom", Geometry(srid=4326), nullable=True),
    Column("properties", JSONB, nullable=True),
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
        TSVector(),
        Computed("to_tsvector('english', properties)", persisted=True),
    ),
    Index("ix_properties_fts", "fts", postgresql_using="gin"),
)
