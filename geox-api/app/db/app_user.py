"""Functions to get and set app user and org settings."""
from typing import Optional
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.engine.cursor import CursorResult

# Postgres allows custom settings
# https://www.postgresql.org/docs/current/runtime-config-custom.html


def set_app_user_id(
    conn: Connection, user_id: Optional[int], local: bool = False
) -> CursorResult:
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
    stmt = text("SELECT nullif(current_setting('app.user_id', TRUE), '')")
    res = conn.execute(stmt).scalar()
    return res if res else None


# Org id
def set_app_user_org(conn: Connection, org_id: UUID, local: bool = True) -> None:
    """Reset Postgres setting ``app.user_id`` to ``user_id``."""
    scope = "LOCAL" if local else "SESSION"
    stmt = text(f"SET {scope} app.user_org = :org_id")
    conn.execute(stmt, {"org_id": str(org_id)})


def unset_app_user_org(conn: Connection, local: bool = False) -> None:
    """Reset Postgres setting ``app.user_id`` to ``user_id``."""
    scope = "LOCAL" if local else "SESSION"
    stmt = text(f"SET {scope} app.user_org = DEFAULT")
    conn.execute(stmt)


def get_app_user_org(conn: Connection) -> Optional[UUID]:
    """Reset Postgres setting ``app.user_id`` to ``user_id``."""
    stmt = text("SELECT nullif(current_setting('app.user_org', TRUE), '')")
    res = conn.execute(stmt).scalar()
    return UUID(res) if res else None
