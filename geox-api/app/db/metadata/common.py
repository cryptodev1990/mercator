"""Common classes used by the SQL tables."""
from datetime import datetime
from typing import Dict, List, Type, Union

from sqlalchemy import Column, DateTime, MetaData, func, Constraint
from sqlalchemy.dialects.postgresql import UUID, ExcludeConstraint

__all__ = ["metadata"]

NAMING_CONVENTION: Dict[Union[str, Type[Constraint]], str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_`%(constraint_name)s`",
        "pk": "pk_%(table_name)s",
        ExcludeConstraint: "ex_%(table_name)s_%(column_0_name)s"
      }
"""Naming convention to use.

The naming convention to apply when naming constraints.

The chosen naming convention is the naming convention suggeted in both the
`Alembic <https://alembic.sqlalchemy.org/en/latest/naming.html>`__  and  `SQlAlchemy <https://docs.sqlalchemy.org/en/14/core/constraints.html#constraint-naming-conventions>`__ docs.

This constraint naming convention differs from the one used by Postgresql.
The reason a namving convetion for postgresql default names was not used is that
it is not documented.

- https://learnsql.com/cookbook/what-is-the-default-constraint-name-in-postgresql/#:~:text=How%20are%20the%20default%20names,)%2C%20and%20'%20pkey%20'.
- https://dev.to/jdheywood/applying-a-naming-convention-to-constraints-via-sqlalchemy--alembic-45e8
"""

# Postgresql defaults are similar to
# NAMING_CONVENTION: Dict[str, str] = {
#     naming_convention={
#         "ix": "%(column_0_label)s_idx",
#         "uq": "%(table_name)s_%(column_0_N_name)s_key",
#         "ck": "%(table_name)s_%(column_0_N_name)s_check",
#         "fk": "%(table_name)s_%(column_0_N_name)s_fkey",
#         "pk": "%(table_name)s_pkey"
#         ExcludeConstraint:"%(table_name)s_%(column_0_N_names)s_excl"
#       }

metadata: MetaData = MetaData(naming_convention=NAMING_CONVENTION)
"""Object describing the app database."""

def TimestampMixin() -> List[Column]:
    return [
        Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
        Column(
            "updated_at",
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
        ),
    ]


def UUIDMixin() -> List[Column]:
    """UUID columns."""
    return [
        Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            server_default=func.gen_random_uuid(),
        )
    ]
