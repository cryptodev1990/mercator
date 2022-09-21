from lib2to3.pytree import Base
import logging
import re
from sqlite3 import connect
from typing import Any, Mapping, Optional
from pydantic import BaseSettings, SecretStr, Field, FilePath
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives import serialization
from io import StringIO

import dotenv
import jinja2 as j2
import typer
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine, create_engine
from snowflake.sqlalchemy import URL

logger = logging.getLogger(__name__)

ENV = j2.Environment(
    loader=j2.PackageLoader("mercator_snowflake", package_path="sql"),
    undefined=j2.StrictUndefined,
)

class Settings(BaseSettings):
    # snowflake_private_key_path: Optional[FilePath]
    # snowflake_private_key_passphrase: Optional[SecretStr]
    snowflake_database: Optional[str]
    snowflake_password: Optional[SecretStr]
    snowflake_schema: Optional[str]
    snowflake_account: str
    snowflake_warehouse: str
    snowflake_role: str
    snowflake_user: str
    snowflake_authenticator: str = Field("snowflake")

    class Config:
        env_file = '.env'

def get_settings():
    return Settings()

def create_snowflake_engine(settings: Settings):
    pkb: Optional[bytes] = None
    # if settings.snowflake_private_key_path:
    #     with open(settings.snowflake_private_key_path, "rb") as key:
    #         private_key_passphrase = settings.snowflake_private_key_passphrase.get_secret_value().encode() if settings.snowflake_private_key_passphrase else None
    #         p_key= serialization.load_pem_private_key(
    #             key.read(),
    #             password=private_key_passphrase,
    #             backend=default_backend())

    #         pkb = p_key.private_bytes(
    #             encoding=serialization.Encoding.DER,
    #             format=serialization.PrivateFormat.PKCS8,
    #             encryption_algorithm=serialization.NoEncryption())

    url = URL(
        user=settings.snowflake_user,
        account=settings.snowflake_account,
        password=settings.snowflake_password.get_secret_value() if settings.snowflake_password else None,
        warehouse=settings.snowflake_warehouse,
        database=settings.snowflake_database,
        schema=settings.snowflake_schema,
        role=settings.snowflake_role
    )
    connect_args = {}
    if pkb is not None:
        connect_args["private_key"] = pkb
    return create_engine(url, connect_args=connect_args, future=True)


def get_sql(
    name: str,
    data: Mapping[str, Any],
) -> str:
    tmpl = ENV.get_template(name)
    rendered = tmpl.render(**data)
    return rendered


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
