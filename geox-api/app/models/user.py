from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
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
