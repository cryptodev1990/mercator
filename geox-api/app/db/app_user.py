from typing import Any, Optional, Union, overload

from sqlalchemy import DDL, text
from sqlalchemy.engine import Connection
from sqlalchemy.engine.cursor import CursorResult, LegacyCursorResult
from sqlalchemy.orm import Session

# Postgres allows custom settings
# https://www.postgresql.org/docs/current/runtime-config-custom.html


def set_app_user_id( conn: Connection, user_id: Optional[int], local: bool = False) -> CursorResult:
    """Set Postgres setting ``app.auth_user_id`` to ``auth_user_id``."""
    scope = "LOCAL" if local else "SESSION"
    stmt = text(f"SET {scope} app.user_id = :user_id")
    return conn.execute(stmt, {"user_id": str(user_id)})


def unset_app_user_id(conn: Connection, local: bool = False) -> CursorResult:
    """Reset Posrgres setting ``app.auth_user_id`` to default."""
    scope = "LOCAL" if local else "SESSION"
    stmt = text(f"SET {scope} app.user_id = DEFAULT")
    return conn.execute(stmt)


def get_app_user_id(conn: Connection) -> Optional[str]:
    """Reset Postgres setting ``app.auth_user_id`` to ``auth_user_id``."""
    stmt = text(f"SELECT nullif(current_setting('app.user_id', TRUE), '')")
    res = conn.execute(stmt).scalar()
    return res if res else None
