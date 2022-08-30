from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, text
from sqlalchemy.dialects.postgresql import UUID

"""Mixin classes used by the model classes."""
from app.db.base_class import Base
from sqlalchemy.orm import declarative_mixin


@declarative_mixin
class TimestampMixin:
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

@declarative_mixin
class UUIDMixin:
    __abstract__ = True
    id = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
