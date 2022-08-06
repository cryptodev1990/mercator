"""Imports all the models, so that Base has them before being imported by Alembic."""

from app.db.base_class import Base  # noqa
from app.models.db_credential import DbCredential  # noqa
from app.models.namespace import Namespace, NamespaceMember  # noqa
from app.models.organization import Organization, OrganizationMember  # noqa
from app.models.shape import Shape  # noqa
from app.models.user import User  # noqa
