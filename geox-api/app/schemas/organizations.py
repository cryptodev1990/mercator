import datetime
from typing import Optional

from pydantic import Field

from app.schemas.common import BaseModel

# This is imported by __init__ with *
# Append all objects to exported in __all__
__all__ = ["Organization"]


class Organization(BaseModel):
    """Represents an Organization."""

    name: str = Field(..., description="Organization name")
    created_by_uesr_id: int
    deleted_at: Optional[datetime.datetime]
    is_personal: bool = Field(False)
    s3_export_enabled: bool = Field(False)
    snowflake_account_id: Optional[str]
