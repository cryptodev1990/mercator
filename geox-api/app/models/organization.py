from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import backref, relationship

from app.models.common import MembershipMixin, TimestampMixin, UUIDMixin


class Organization(TimestampMixin, UUIDMixin):
    __tablename__ = "organizations"

    name = Column(String, nullable=False)
    deleted_at = Column(DateTime)


class OrganizationMember(TimestampMixin, MembershipMixin):
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True, index=True)

    # FOR NOW, only one organization per user
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        unique=True,
    )
    # https://stackoverflow.com/questions/5033547/sqlalchemy-cascade-delete
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    added_by_user_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # https://stackoverflow.com/questions/7548033/how-to-define-two-relationships-to-the-same-table-in-sqlalchemy
    user = relationship(
        "User",
        backref=backref(
            "OrganizationMember", passive_deletes=True, cascade="all,delete"
        ),
        foreign_keys=[user_id],
    )
    added_by_user = relationship("User", foreign_keys=[added_by_user_id])
    organization = relationship("Organization", foreign_keys=[organization_id])
    UniqueConstraint("user_id", "organization_id")
