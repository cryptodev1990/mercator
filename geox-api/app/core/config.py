"""App settings and configuration management."""
import logging
import os
from asyncio.log import logger
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, cast

from git.repo import Repo

# pylint: disable=no-name-in-module
from pydantic import (
    BaseModel,
    BaseSettings,
    EmailStr,
    Field,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    root_validator,
    validator,
)

# pylint: enable=no-name-in-module
from timvt.db import PostgresSettings as TimVTPostgresSettings

from app.core.datatypes import (
    AnyHttpURLorAsterisk,
    AppEnvEnum,
    GitCommitHash,
    LogLevel,
    S3Url,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

__VERSION__ = "0.0.1"

DEFAULT_DOMAIN = "mercator.tech"
DEFAULT_MACHINE_ACCOUNT_EMAIL = f"duber+ManagementApi@{DEFAULT_DOMAIN}"
CONTACT_EMAIL = f"founders@{DEFAULT_DOMAIN}"


class EngineOptions(BaseModel):
    """SQLAlchemy Engine Settings.

    Subset of options that are passed to SQLAlchemy :func:`sqlalchemy.create_engine`
    when initializing the app engine.

    See https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine.

    """

    echo: bool = False
    echo_pool: bool = False
    pool_timeout: int = Field(30, ge=1)
    pool_recycle: int = -1
    # SQLAlchemy default is 5
    pool_size: int = Field(10, ge=1)
    # SQLAlchemy default is 10
    max_overflow: int = Field(20, ge=0)


class TilerPoolOptions(BaseModel):
    """Options for the tiler pool.

    These are used by :func:`get_tiler_settings`, and are used to initialize :class:`TimVTPostgresSettings`.

    All defaults are those in :class:`TimVTPostgresSettings`.

    """

    db_min_conn_size: int = 1
    db_max_conn_size: int = 10
    db_max_queries: int = 50000
    db_max_inactive_conn_lifetime: float = 300


class CacheOptions(BaseModel):
    """Options for the user/organization cache.

    The cache is defined in app.dependencies.Cache. It caches user and organization
    info for each request.
    """

    enabled: bool = Field(
        True, description="If true, then use a cache. If false, no cache."
    )
    timeout: int = Field(3600, ge=0, description="Cache key default timeout in seconds.")


class Settings(BaseSettings):
    """Config settings."""

    app_name: str = Field("geox_api", env="APP_NAME")
    version: str = Field(__VERSION__, description="App version number", env="APP_VERSION")
    app_secret_key: SecretStr = Field(...)

    # Auth For JWT
    # These properties are confusing because the env variable name != property names
    auth_client_id: str = Field(..., env="AUTH0_CLIENT_ID")
    auth_client_secret: SecretStr = Field(..., env="AUTH0_CLIENT_SECRET")
    management_client_id: str = Field(..., env="AUTH0_MACHINE_CLIENT_ID")
    management_client_secret: SecretStr = Field(..., env="AUTH0_MACHINE_CLIENT_SECRET")
    auth_domain: str = Field(..., env="AUTH0_DOMAIN")
    auth_audience: str = Field(..., env="AUTH0_API_AUDIENCE")
    # TODO: AUTH0_ALGORITHMS should be an enum/literal set
    auth_algorithms: str = Field("RS256", env="AUTH0_ALGORITHMS")

    # Bucket to use for data exports
    aws_s3_url: Optional[S3Url] = Field(
        None,
        description="S3 used to store export data, e.g. 's3://bucket/path/as/prefix/'",
    )

    # Stripe API key
    stripe_api_key: Optional[str] = Field(None, env="STRIPE_API_KEY")
    stripe_webhook_secret: Optional[str] = Field(None, env="STRIPE_WEBHOOK_SECRET")
    skip_stripe: Optional[bool] = Field(None, env="SKIP_STRIPE")

    # Sendgrid API key
    sendgrid_api_key: Optional[str] = Field(None, env="SENDGRID_API_KEY")

    # Email approved by Sendgrid for sending automated emails
    # Configure this at https://app.sendgrid.com/settings/sender_auth/senders
    sendgrid_sender_email: Optional[EmailStr] = Field(
        EmailStr("founders@mercator.tech"), env="SENDGRID_SENDER_EMAIL"
    )

    # Webhook secret for external communication to our email endpoint
    email_webhook_secret: Optional[SecretStr] = Field(None, env="EMAIL_WEBHOOK_SECRET")

    # Datadog config
    dd_api_key: str = Field("", env="DD_API_KEY")
    dd_app_key: str = Field("", env="DD_APP_KEY")
    dd_enabled: bool = str(Field("false", env="DD_ENABLED")).lower() == "true"

    # Datadog initialization config
    dd_init_kwargs: Dict[str, Any] = {}
    if dd_enabled:
        dd_init_kwargs.update({"api_key": dd_api_key, "app_key": dd_app_key})

    # pylint: disable=no-self-argument
    @root_validator
    def _validate_dd_config(cls, values):
        if values["dd_enabled"] and (
            not values["dd_api_key"] or not values["dd_app_key"]
        ):
            raise ValueError(
                "DataDog APP key (DD_APP_KEY) and API key (DD_API_KEY) are required when DataDog is enabled (DD_ENABLED=true)"
            )
        return values

    # pylint: enable=no-self-argument

    # pylint: disable=no-self-argument
    @validator("aws_s3_url", pre=True)
    def _validate_aws_s3_url(cls, v):  # pylint: disable=no-self-argument
        """Ensure the S3 URL always ends with a backslash."""
        if v and not v.endswith("/"):
            v = f"{v}/"
        return v

    # pylint: enable=no-self-argument

    aws_s3_upload_access_key_id: Optional[str] = Field(
        None, env="AWS_S3_UPLOAD_ACCESS_KEY_ID"
    )
    aws_s3_upload_secret_access_key: Optional[SecretStr] = Field(
        None, env="AWS_S3_UPLOAD_SECRET_ACCESS_KEY"
    )

    machine_account_email: EmailStr = Field(cast(EmailStr, DEFAULT_MACHINE_ACCOUNT_EMAIL))
    contact_email: EmailStr = Field(cast(EmailStr, CONTACT_EMAIL))

    # pylint: disable=no-self-argument
    @validator("machine_account_email")
    def _validate_machine_account_email(
        cls, v: str  # pylint: disable=no-self-argument
    ) -> str:
        if not v.endswith(f"@{DEFAULT_DOMAIN}"):
            raise ValueError(f"Machine account email must end with {DEFAULT_DOMAIN}")
        return v

    # pylint: enable=no-self-argument

    @property
    def machine_account_sub_id(self) -> str:
        """Machine account sub id."""
        return f"{self.management_client_id}@clients"

    backend_cors_origins: Tuple[AnyHttpURLorAsterisk] = Field(
        cast(Tuple[AnyHttpURLorAsterisk], tuple(["*"])),
        description="""Values of CORS access-control-allow-origins header

    The setting is a list of URLs. In addition, the input accepts the following values:

    In an environment variable, this must be set as a JSON encoded array, for example: `["http://localhost.tiangolo.com", "https://localhost.tiangolo.com", "http://localhost", "http//localhost:8080"]`
    """,
    )

    # pylint: disable=no-self-argument
    @validator("backend_cors_origins", pre=True)
    def _assemble_cors_origins(cls, v):  # pylint: disable=no-self-argument
        # Note - pre validation is done AFTER environment variable parsing
        # environment variables are parsed as JSON.
        # See https://pydantic-docs.helpmanual.io/usage/settings/#parsing-environment-variable-values for what to do
        # to handle comma-separated values as inputs
        if v is None or v == "":
            return tuple(["*"])
        return v

    # pylint: enable=no-self-argument

    # db connection info
    # These are named so that the same environment variables can be used between the postgres docker container
    # and the app without changes
    postgres_db: Optional[str] = Field("geox")
    postgres_user: Optional[str] = Field("postgres")
    postgres_server: Optional[str] = Field("localhost")
    postgres_password: Optional[SecretStr] = Field(None)
    postgres_port: int = Field(5432)
    # If provided POSTGRES_CONNECTION will be override the individual postgres components
    sqlalchemy_database_uri: Optional[PostgresDsn] = Field(
        None, env="POSTGRES_CONNECTION"
    )

    engine_opts: EngineOptions = Field(
        EngineOptions(),  # type: ignore
        description="Options to apply to the app database SQLAlchemy engine.",
    )

    worker_engine_opts: EngineOptions = Field(
        EngineOptions(),  # type: ignore
        description="Options to apply to the connections used by Celery workers to access the app database.",
    )

    # pylint: disable=no-self-argument
    # validation is done in the order fields are defined. sqlalchemy_database_uri
    # needs to be defined after its subcomponents
    @validator("sqlalchemy_database_uri", pre=True)
    def _validate_sqlalchemy_database_uri(
        cls, v: Optional[str], values: Dict[str, Any]  # pylint: disable=no-self-argument
    ) -> Any:
        """Return the SQLAlchemy database URI."""
        # Treat None and empty string as existence
        if v:
            return str(v)
        dsn = PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("postgres_user"),
            password=str(values.get("postgres_password", "")),
            host=cast(str, values.get("postgres_server")),
            port=str(values.get("postgres_port")),
            path=f"/{values.get('postgres_db', '')}",
        )
        return dsn

    # pylint: enable=no-self-argument

    sqlalchemy_osm_database_uri: Optional[PostgresDsn] = Field(
        None, env="SQLALCHEMY_OSM_DATABASE_URI"
    )

    tiler_pool_options: TilerPoolOptions = Field(
        default_factory=TilerPoolOptions,
        description="Options for the tiling server connection pool.",
    )

    redis_connection: RedisDsn = Field(
        cast(RedisDsn, "redis://localhost:6379/0"),
        description="Redis connection info that can be used for celery and the cache.",
    )

    cache: CacheOptions = Field(
        CacheOptions(enabled=True),  # type: ignore
        description="Cache options.",
        env="APP_CACHE",
    )

    git_commit: Optional[GitCommitHash] = Field(
        None, description="Git commit of the app source code being used."
    )  # type: ignore

    # pylint: disable=no-self-argument
    @validator("git_commit", pre=True, always=True)
    def _validate_git_commit(cls, v):  # pylint: disable=no-self-argument
        # Case in which GIT_COMMIT exists - treat empty string as non-existence
        if v:
            return str(v).lower()
        # Case in which GIT_COMMIT does not exist
        try:
            # TODO: be more careful about where this is searching and handling specific errors
            git_repo = Repo(Path(__file__).resolve(), search_parent_directories=True)
            if git_repo.is_dirty():
                logger.warning(
                    "Git repo is dirty. The setting `git_commit` does not reflect local changes."
                )
            branch = str(git_repo.active_branch.commit).lower()
            return branch
        except Exception:  # pylint: disable=broad-except
            return None

    # pylint: enable=no-self-argument

    app_env: AppEnvEnum = Field(AppEnvEnum.dev)
    app_log_level: LogLevel = Field(LogLevel.INFO, describe="Log level")
    worker_id_length: int = Field(
        8, describe="Length of the generated random worker ID", env_var="WORKER_ID_LENGTH"
    )

    # pylint: disable=no-self-argument
    @validator("app_env", pre=True)
    def _validate_app_env(cls, v) -> str:  # pylint: disable=no-self-argument
        v = str(v).lower()
        return v

    # pylint: enable=no-self-argument

    class Config:  # noqa
        env_file = ".env"
        # environment variables for fields are case insensitive
        case_sensitive = False
        # nested model env variables use {field_name}__{submodel_field_name}
        # for example, APP_CACHE__TIMEOUT=84600
        env_nested_delimiter = "__"
        # if settings are frozen, then they are hashable and can be cached.
        allow_mutation = False
        frozen = True


@lru_cache()
def get_settings() -> Settings:
    """Return the app settings object."""
    # This allows specifying the source of environment variables via an env file
    # See https://pydantic-docs.helpmanual.io/usage/settings/#dotenv-env-support
    env_file: Optional[str] = os.environ.get("ENV_FILE", ".env")
    if env_file and os.path.isfile(env_file):
        return Settings(_env_file=env_file)  # type: ignore
    return Settings()  # type: ignore


@lru_cache()
def get_tiler_settings() -> TimVTPostgresSettings:
    settings = get_settings()
    password = (
        settings.postgres_password.get_secret_value()
        if settings.postgres_password
        else ""
    )
    return TimVTPostgresSettings(
        postgres_host=settings.postgres_server,
        postgres_port=str(settings.postgres_port),
        postgres_user=settings.postgres_user,
        postgres_pass=password,
        postgres_dbname=settings.postgres_db,
        **settings.tiler_pool_options.dict(),
        db_tables=None,
    )
