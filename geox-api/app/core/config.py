"""App settings and configuration management."""
import logging
import os
from asyncio.log import logger
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Dict, List, Literal, Optional, Union

from pydantic import (
    AnyHttpUrl,
    AnyUrl,
    BaseSettings,
    EmailStr,
    Field,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    constr,
    validator,
)
from sqlalchemy import desc

logger = logging.getLogger(__name__)

__VERSION__ = "0.0.1"

DEFAULT_DOMAIN = "mercator.tech"
DEFAULT_MACHINE_ACCOUNT_EMAIL = f"duber+ManagementApi@{DEFAULT_DOMAIN}"
CONTACT_EMAIL = f"founders@{DEFAULT_DOMAIN}"

AnyHttpURLorAsterisk = Union[AnyHttpUrl, Literal["*"]]
"""A valid HTTP URL or *."""
# used in CORS types

GitCommitHash = Annotated[
    str,
    constr(
        min_length=40,
        max_length=40,
        regex="^[0-9a-fA-F]{40}$",
        strict=True,
        to_lower=True,
        strip_whitespace=True,
    ),
]
"""Pydantic type to validate git hashes."""


class S3Url(AnyUrl):
    """Validate an S3 URI type.

    Example: ``s3://bucket-name/path/to/file``.

    """

    allowed_schemes = {
        "s3",
    }
    host_required = True

    __slots__ = ()


class Settings(BaseSettings):
    """Config settings."""

    version: str = Field(
        __VERSION__, description="App version number", env="APP_VERSION"
    )
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

    @validator("aws_s3_url", pre=True)
    def _validate_aws_s3_url(cls, v):
        """Ensure the S3 URL always ends with a backslash."""
        if v and not v.endswith("/"):
            v = f"{v}/"
        return v

    aws_s3_upload_access_key_id: Optional[str] = Field(
        None, env="AWS_S3_UPLOAD_ACCESS_KEY_ID"
    )
    aws_s3_upload_secret_access_key: Optional[SecretStr] = Field(
        None, env="AWS_S3_UPLOAD_SECRET_ACCESS_KEY"
    )

    machine_account_email: EmailStr = Field(DEFAULT_MACHINE_ACCOUNT_EMAIL)
    contact_email: EmailStr = Field(CONTACT_EMAIL)

    @validator("machine_account_email")
    def _validate_machine_account_email(cls, v: str) -> str:
        if not v.endswith(f"@{DEFAULT_DOMAIN}"):
            raise ValueError(f"Machine account email must end with {DEFAULT_DOMAIN}")
        return v

    @property
    def machine_account_sub_id(self) -> str:
        """Machine account sub id."""
        return f"{self.management_client_id}@clients"

    backend_cors_origins: List[AnyHttpURLorAsterisk] = Field(
        ["*"], description="Valid CORS origin domains."
    )

    @validator("backend_cors_origins", pre=True)
    def _assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if v is None:
            return ["*"]
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

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

    sqlalchemy_osm_database_uri: Optional[PostgresDsn] = Field(
        None, env="SQLALCHEMY_OSM_DATABASE_URI"
    )

    # validation is done in the order fields are defined. sqlalchemy_database_uri
    # needs to be defined after its subcomponents
    @validator("sqlalchemy_database_uri", pre=True)
    def _validate_sqlalchemy_database_uri(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Any:
        """Return the SQLAlchemy database URI."""
        # Treat None and empty string as existence
        if v:
            return str(v)
        dsn = PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("postgres_user"),
            password=str(values.get("postgres_password", "")),
            host=values.get("postgres_server"),
            port=str(values.get("postgres_port")),
            path=f"/{values.get('postgres_db', '')}",
        )
        return dsn

    redis_connection: RedisDsn = Field(
        "redis://localhost:6379/0", description="Redis DSN to use for celery"
    )

    git_commit: Optional[GitCommitHash] = Field(
        None, description="Git commit of the app source code being used."
    )  # type: ignore

    @validator("git_commit", pre=True, always=True)
    def _validate_git_commit(cls, v):
        # Case in which GIT_COMMIT exists - treat empty string as non-existence
        if v:
            return str(v).lower()
        # Case in which GIT_COMMIT does not exist
        try:
            import git

            # TODO: be more careful about where this is searching and handling specific errors
            git_repo = git.Repo(
                Path(__file__).resolve(), search_parent_directories=True
            )
            if git_repo.is_dirty():
                logger.warning(
                    "Git repo is dirty. The git commit does not reflect local changes."
                )
            branch = str(git_repo.active_branch.commit).lower()
            return branch
        except:
            return None

    class Config:  # noqa
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return the app settings object."""
    # This allows specifying the source of environment variables via an env file
    # See https://pydantic-docs.helpmanual.io/usage/settings/#dotenv-env-support
    env_file: Optional[str] = os.environ.get("ENV_FILE", ".env")
    if env_file and os.path.isfile(env_file):
        return Settings(_env_file=env_file)  # type: ignore
    return Settings()
