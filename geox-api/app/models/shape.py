from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from sqlalchemy_json import mutable_json_type

from .db import Base


class Shape(Base):
    __tablename__ = "shapes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    edited_at = Column(DateTime, default=func.now())
    edited_by_user_id = Column(Integer, ForeignKey("users.id"))
    shape = Column(mutable_json_type(dbtype=JSONB, nested=True))
