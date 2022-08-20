import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, func

from app.db.base_class import Base


class Webhook(Base):
    """Represents a webhook."""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    webhook_uri = Column(String, nullable=False)
    request_args = Column(JSON, nullable=False)
    belongs_to_organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    updated_at = Column(DateTime, default=func.now(), onupdate=datetime.datetime.now)
    updated_by_user_id = Column(Integer, ForeignKey("users.id"))
