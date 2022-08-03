"""Database credentials model"""
import datetime
import uuid
from typing import Any, Dict

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, null
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql import func

from app.db.base_class import Base


class DbCredential(Base):
    __tablename__ = "db_credentials"

    uuid = Column(
        UUID(as_uuid=True), primary_key=True, default=lambda _: str(uuid.uuid4())
    )
    name = Column(String, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    is_default = Column(Boolean)
    created_at = Column(DateTime, default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=func.now(), onupdate=datetime.datetime.now)
    updated_by_user_id = Column(Integer, ForeignKey("users.id"))
    db_driver = Column(String, nullable=False)
    # DB credentials - encrypted
    db_user = Column(String, nullable=False)
    db_password = Column(String, nullable=False)
    db_host = Column(String, nullable=False)
    db_port = Column(String, nullable=False)
    db_database = Column(String, nullable=False)
    db_extras = Column(String, nullable=True)
