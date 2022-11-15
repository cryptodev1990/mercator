"""Setup geofencer Snowflake share ETL for an organization."""
import logging
import re
import uuid
from io import StringIO
from typing import Any, Generator, List

import typer
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.engine.row import Row

from .utils import Settings, create_snowflake_engine, get_settings, get_sql

logger = logging.getLogger(__name__)

MERCATOR_ORG_ID = uuid.UUID("E6CEF492506946D38431FDA523CAF2F6")


def render_sql(template_name: str, row: Row) -> str:
    """Create Snowflake share information."""
    m = re.match(
        r"^[A-Z]{7}\.[A-Z0-9]{7}\.(?P<dev>DEV_)?ORG_(?P<org_id>[A-F0-9]{32})_SHARE$",
        row["name"],
    )
    if not m:
        raise ValueError(f"Invalid share name: {row['name']}")
    safe_org_id = m.group("org_id")
    org_id = str(uuid.UUID(safe_org_id))
    is_dev = bool(m.group("dev"))
    s3_int = "S3_INT_DEV" if is_dev else "S3_INT"
    error_int = "SNOWPIPE_SNS_INT"
    params = {
        "dev": is_dev,
        "s3_int": s3_int,
        "error_int": error_int,
        "safe_org_id": safe_org_id,
        "org_id": org_id,
        "share_name": row["name"],
        "db_name": row["database_name"],
    }
    sql = get_sql(f"{template_name}.sql.j2", params)
    return sql


def filter_shares(
    row,
    include_dev: bool = True,
    include_mercator: bool = True,
    include_customers: bool = True,
) -> bool:
    if row["kind"] != "OUTBOUND":
        return False
    m = re.match(
        r"^[A-Z]{7}\.[A-Z0-9]{7}\.(?P<dev>DEV_)?ORG_(?P<org_id>[A-F0-9]{32})_SHARE$",
        row["name"],
    )
    if not m:
        return False
    if m.group("dev"):
        return include_dev
    if uuid.UUID(m.group("org_id")) == MERCATOR_ORG_ID:
        return include_mercator
    return include_customers


def get_db_shares(
    conn: Connection,
    include_customers: bool = True,
    include_dev: bool = True,
    include_mercator: bool = True,
) -> List[Row]:
    return [
        row
        for row in conn.execute(text("SHOW SHARES"))
        if filter_shares(
            row,
            include_customers=include_customers,
            include_dev=include_dev,
            include_mercator=include_mercator,
        )
    ]


def execute_script(conn: Connection, script: str) -> Generator[Any, None, None]:
    for cur in conn.connection.execute_stream(StringIO(script)):  # type: ignore
        for ret in cur:
            yield (cur, ret)


def run(
    settings: Settings,
    template_name: str,
    include_customers: bool = True,
    include_dev: bool = True,
    include_mercator: bool = True,
) -> None:
    engine = create_snowflake_engine(settings)
    with engine.begin() as conn:  # type: ignore
        conn.execute(text("USE ROLE geofencer_etl_role"))
        shares = get_db_shares(
            conn,
            include_customers=include_customers,
            include_dev=include_dev,
            include_mercator=include_mercator,
        )
        for row in shares:
            logger.info("Migrating: %s", row['name'])
            sql = render_sql(template_name, row)
            logger.debug(sql)
            for _ in execute_script(conn, sql):
                pass


def main(
    template_name: str,
    include_customers: bool = True,
    include_dev: bool = True,
    include_mercator: bool = True,
) -> None:
    """Create Snowflake share information."""
    settings = get_settings()
    run(
        settings,
        template_name,
        include_customers=include_customers,
        include_dev=include_dev,
        include_mercator=include_mercator,
    )


if __name__ == "__main__":
    typer.run(main)
