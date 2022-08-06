from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.models.common import MembershipMixin, TimestampMixin


class Namespace(TimestampMixin):
    __tablename__ = "namespaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    organization_id = Column(UUID, ForeignKey("organizations.id"), nullable=True)


class NamespaceMember(TimestampMixin, MembershipMixin):
    __tablename__ = "namespace_members"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    namespace_id = Column(
        Integer, ForeignKey("namespaces.id"), nullable=False, index=True
    )
    added_by_user_id = Column(
        Integer, ForeignKey("users.id"), nullable=True, index=True
    )
    CheckConstraint("user_id", "namespace_id")
