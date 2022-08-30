"""Shape model."""
import datetime
import uuid
from typing import Any, Dict

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, null, text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class Shape(Base):
    """A geospatial shape."""

    __tablename__ = "shapes"

    uuid = Column(
        UUID(as_uuid=True), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    name = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=func.now(), onupdate=datetime.datetime.utcnow)
    updated_by_user_id = Column(Integer, ForeignKey("users.id"))
    deleted_at = Column(DateTime, nullable=True)
    deleted_at_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    geojson = Column(JSON, nullable=False)
    organization_id = Column(UUID, ForeignKey("organizations.id"))

    # TODO: If Pydantic basemodel was used, then dict is already used. See https://pydantic-docs.helpmanual.io/usage/models/
    def as_dict(self) -> Dict[str, Any]:
        """Return dict."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    __mapper_args__ = {"eager_defaults": True}
