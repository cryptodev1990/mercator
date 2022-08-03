import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from app.db.base_class import Base


class Namespace(Base):
    __tablename__ = "namespaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=datetime.datetime.utcnow)


class NamespaceMember(Base):
    __tablename__ = "namespace_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    namespace_id = Column(
        Integer, ForeignKey("namespaces.id"), nullable=False, index=True
    )
    added_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    has_read = Column(Boolean, nullable=False, default=False)
    has_write = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=datetime.datetime.now)
