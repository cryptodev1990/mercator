"""User-defined unctions defined for SQLAlchemy.

See https://docs.sqlalchemy.org/en/14/core/functions.html#sqlalchemy.sql.functions.GenericFunction
"""

from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import UUID


class app_user_id(GenericFunction):
    """Function app_user_id()."""

    type = Integer()
    inherit_cache = True


class app_user_org(GenericFunction):
    """Function app_user_org()."""

    type = UUID(as_uuid=True)
    inherit_cache = True
