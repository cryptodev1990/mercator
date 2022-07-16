"""App settings and configuration management."""
import hashlib
import os
from functools import lru_cache
from typing import Optional, List, Union, Literal, Dict, Any

from pydantic import AnyHttpUrl, BaseSettings, Field, PostgresDsn, EmailStr, validator
from sqlalchemy import desc


DEFAULT_DOMAIN = "mercator.tech"
DEFAULT_MACHINE_ACCOUNT_EMAIL = f"duber+ManagementApi@{DEFAULT_DOMAIN}"

AnyHttpURLorAsterisk = Union[AnyHttpUrl, Literal["*"]]
"""A valid HTTP URL or *."""
# used in CORS types


class Settings(BaseSettings):
    """Config settings."""

    # Auth For JWT
    # These proporties are confusing because the env variable name != property names
    auth_client_id: str = Field(..., env="AUTH0_CLIENT_ID")
    auth_client_secret: str = Field(..., env="AUTH0_CLIENT_SECRET")
    management_client_id: str = Field(..., env="AUTH0_MACHINE_CLIENT_ID")
    management_client_secret: str = Field(..., env="AUTH0_MACHINE_CLIENT_SECRET")
    auth_domain: str = Field(..., env="AUTH0_DOMAIN")
    auth_audience: str = Field(..., env="AUTH0_API_AUDIENCE")
    # TODO: AUTH0_ALGORITHMS should be an enum/literal set
    auth_algorithms: str = Field("RS256", env="AUTH0_ALGORITHMS")

    machine_account_email: EmailStr = Field(DEFAULT_MACHINE_ACCOUNT_EMAIL)

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

    app_secret_key: str

    frontend_url: AnyHttpUrl = Field(..., description="URL that the frontend uses.")

    # db connection info
    # These are named so that the same environment variables can be used between the postgres docker container
    # and the app without changes
    postgres_db: Optional[str] = Field(None)
    postgres_user: Optional[str] = Field(None)
    postgres_server: Optional[str] = Field(None)
    postgres_password: Optional[str] = Field(None)
    postgres_port: int = Field(5432)
    # If provided POSTGRES_CONNECTION will be override the individual postgres components
    sqlalchemy_database_uri: Optional[PostgresDsn] = Field(
        None, env="POSTGRES_CONNECTION"
    )

    @validator("sqlalchemy_database_uri", pre=True)
    def _validate_sqlalchemy_database_uri(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Return the SQLAlchemy database URI."""
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+psycopg2",
            user=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_server"),
            port=str(values.get("postgres_port")),
            path=f"/{values.get('postgres_db', '')}",
        )
    # validateion is done in the order fields are defined. sqlalchemy_database_uri
    # needs to be defined after everything

    class Config:  # noqa
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def _get_settings(env_file: Optional[str], env_file_hash: str) -> Settings:
    return Settings(_env_file=env_file)  # type: ignore


def get_settings() -> Settings:
    """Return the app settings object."""
    # This allows specifying the source of environment variables via an env file
    # See https://pydantic-docs.helpmanual.io/usage/settings/#dotenv-env-support
    env_file: Optional[str] = os.environ.get("ENV_FILE", ".env")
    if env_file and os.path.isfile(env_file):
        env_file_hash = (
            hashlib.md5(open(env_file, "rb").read()) if os.path.isfile(env_file) else ""
        )
    else:
        env_file_hash = ""
        env_file = None
    # Using an inner function will cache on the *contents* of the settings file,
    # so it will update if that changes. This may be unnecessary - but I think it makes sense.
    return _get_settings(env_file, env_file_hash)
