"""I name this module utils; deal with it."""
from functools import lru_cache
from typing import Any, Mapping, Optional, cast

import jinja2 as j2
from pydantic import BaseSettings, Field, SecretStr  # pylint: disable=no-name-in-module
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from snowflake.sqlalchemy import URL

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
    snowflake_account: str = Field(..., regex="^[A-Z]{7}-[A-Z0-9]{7}$")
    snowflake_warehouse: str
    snowflake_role: str
    snowflake_user: str
    snowflake_authenticator: str = Field("snowflake")

    class Config:
        env_file = ".env"


@lru_cache(None)
def get_settings() -> Settings:
    return Settings()  # type: ignore


def create_snowflake_engine(settings: Settings) -> Engine:
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
        password=settings.snowflake_password.get_secret_value()
        if settings.snowflake_password
        else None,
        warehouse=settings.snowflake_warehouse,
        database=settings.snowflake_database,
        schema=settings.snowflake_schema,
        role=settings.snowflake_role,
    )
    connect_args = {}
    if pkb is not None:
        connect_args["private_key"] = pkb
    return create_engine(url, connect_args=connect_args, future=True)


def get_sql(
    name: str,
    data: Optional[Mapping[str, Any]] = None,
) -> str:
    data_: Mapping[str, Any] = data or {}  # type: ignore
    tmpl = ENV.get_template(name)
    rendered = tmpl.render(**cast(Mapping[str, Any], data_))
    return rendered
