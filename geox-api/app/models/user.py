"""User model"""
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    sub_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    given_name = Column(String)
    family_name = Column(String)
    nickname = Column(String)
    name = Column(String)
    picture = Column(String)
    locale = Column(String)
    updated_at = Column(DateTime)
    email_verified = Column(Boolean)
    iss = Column(String)
    last_login_at = Column(DateTime)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
