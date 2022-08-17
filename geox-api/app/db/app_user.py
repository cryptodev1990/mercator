from typing import Any, Optional, Union, overload

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.engine.cursor import CursorResult, LegacyCursorResult
from sqlalchemy.orm import Session

# Postgres allows custom settings
# https://www.postgresql.org/docs/current/runtime-config-custom.html


@overload
def set_app_user_id(
    session: Session, user_id: Optional[str], local: bool = False
) -> CursorResult:
    ...


@overload
def set_app_user_id(
    session: Connection, user_id: Optional[str], local: bool = False
) -> LegacyCursorResult:
    ...


def set_app_user_id(session, user_id, local=False):
    """Set Postgres setting ``app.auth_user_id`` to ``auth_user_id``."""
    scope = "LOCAL" if local else "SESSION"
    stmt = f"SET {scope} app.auth_user_id = :user_id"
    return session.execute(text(stmt), {"user_id": str(user_id)})


@overload
def unset_app_user_id(session: Session, local: bool = False) -> CursorResult:
    ...


@overload
def unset_app_user_id(session: Connection, local: bool = False) -> LegacyCursorResult:
    ...


def unset_app_user_id(session, local=False) -> CursorResult:
    """Reset Posrgres setting ``app.auth_user_id`` to default."""
    scope = "LOCAL" if local else "SESSION"
    stmt = f"SET {scope} app.auth_user_id = DEFAULT"
    return session.execute(text(stmt))


def get_app_user_id(session: Union[Session, Connection]) -> Optional[str]:
    """Reset Postgres setting ``app.auth_user_id`` to ``auth_user_id``."""
    stmt = f"SELECT nullif(current_setting('app.auth_user_id', TRUE), '')"
    res = session.execute(text(stmt)).scalar()
    return res if res else None
