"""Shape model."""
from typing import Any, Dict

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from geoalchemy2 import Geometry

from app.db.base_class import Base


class Shape(Base):
    """A geospatial shape."""

    __tablename__ = "shapes"

    uuid = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )
    name = Column(String, index=True)
    created_at = Column(
        DateTime, default=func.now(), server_default=func.now(), nullable=False
    )
    created_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        server_default=func.app_user_id(),
    )
    updated_at = Column(DateTime, default=func.now(),
                        server_default=func.now())
    updated_by_user_id = Column(
        Integer,
        ForeignKey("users.id"),
        server_default=func.app_user_id(),
        nullable=False,
    )
    deleted_at = Column(DateTime, nullable=True, index=True)
    deleted_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    geojson = Column(JSONB, nullable=False)
    geom = Column(Geometry(srid=4326), nullable=True)
    properties = Column(JSONB, nullable=True)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        server_default=func.app_user_org(),
        index=True,
        nullable=False,
    )

    __mapper_args__ = {"eager_defaults": True}
