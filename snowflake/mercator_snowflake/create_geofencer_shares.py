"""Setup geofencer Snowflake share ETL for an organization."""
import logging
import re
from io import StringIO

import typer

from .utils import Settings, create_snowflake_engine, get_settings, get_sql

logger = logging.getLogger(__name__)


def run(
    settings: Settings, organization_id: str, snowflake_account_id: str, dev: bool = False
) -> None:
    org_id_safe = re.sub("[^A-Za-z0-9]", "", str(organization_id))
    db_name = f"DEV_ORG_{org_id_safe}" if dev else f"ORG_{org_id_safe}"
    share_name = f"{db_name}_SHARE"
    s3_int = "s3_int_dev" if dev else "s3_int"
    error_int = "snowpipe_sns_int"
    sql = get_sql(
        "geofencer_shares.sql.j2",
        {
            "dev": dev,
            "org_id": organization_id,
            "snowflake_account_id": snowflake_account_id,
            "org_id_safe": org_id_safe,
            "share_name": share_name,
            "db_name": db_name,
            "s3_int": s3_int,
            "error_int": error_int,
            "aws_s3_url": "s3://mercator-geofencer-data/export/shapes/",
        },
    )
    logger.debug(sql)
    engine = create_snowflake_engine(settings)
    with engine.connect() as conn:
        with conn.begin():
            for cur in conn.connection.execute_stream(StringIO(sql)):  # type: ignore
                for _ in cur:
                    pass


def main(organization_id: str, snowflake_account_id: str, dev: bool = False) -> None:
    """Create Snowflake share information."""
    settings = get_settings()
    run(settings, organization_id, snowflake_account_id, dev=dev)


if __name__ == "__main__":
    typer.run(main)
