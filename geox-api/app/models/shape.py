"""Shape model."""
import datetime
import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, null
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class Shape(Base):
    __tablename__ = "shapes"

    uuid = Column(
        UUID(as_uuid=True), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    name = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=func.now(), onupdate=datetime.datetime.now)
    updated_by_user_id = Column(Integer, ForeignKey("users.id"))
    deleted_at = Column(DateTime, nullable=True)
    deleted_at_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    geojson = Column(JSON, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    __mapper_args__ = {"eager_defaults": True}
