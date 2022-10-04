from app.schemas.common import BaseModel
from app.schemas.organizations import Organization
from app.schemas.user import User

__all__ = ["UserOrganization"]

class UserOrganization(BaseModel):
    """Represents the combination of a User and organization.

    The combination of user and organization is the basic information needed by most routes for
    authentication.
    """

    user: User
    organization: Organization
