"""Setup geofencer Snowflake share ETL for an organization."""
import logging
import re
from io import StringIO

import typer

from .utils import get_settings, get_sql, create_snowflake_engine, Settings

logger = logging.getLogger(__name__)


def run(settings: Settings, organization_id: str, snowflake_account_id: str) -> None:
    sql = get_sql(
        "geofencer_shares.sql.j2",
        {
            "org_id": organization_id,
            "snowflake_account_id": snowflake_account_id,
            "org_id_safe": re.sub("[^A-Za-z0-9]", "", str(organization_id)),
            # Url should MUST end in /
            "aws_s3_url": "s3://mercator-geofencer-data/export/shapes/",
        },
    )
    logger.debug(sql)
    engine = create_snowflake_engine(settings)
    with engine.connect() as conn:
        with conn.begin():
            for cur in conn.connection.execute_stream(StringIO(sql)):
                for ret in cur:
                    pass


def main(organization_id: str, snowflake_account_id: str) -> None:
    """Create Snowflake share information."""
    settings = get_settings()
    run(settings, organization_id, snowflake_account_id)


if __name__ == "__main__":
    typer.run(main)
