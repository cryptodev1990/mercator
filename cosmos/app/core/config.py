# pylint: disable=too-few-public-methods
"""App settings and configuration management."""
import logging
from functools import lru_cache
from typing import Optional, Tuple

# pylint: disable=no-name-in-module
from pydantic import BaseModel, BaseSettings, Field, SecretStr

from app.core.datatypes import AppEnvEnum, LogLevel

# pylint: enable=no-name-in-module


__VERSION__ = "0.0.1"

logger = logging.getLogger(__name__)


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


class AppDatabase(BaseModel):
    """Defines the app database settings."""

    engine: Optional[str] = Field("postgresql+asyncpg")
    database: Optional[str] = Field("postgres")
    user: Optional[str] = Field("postgres")
    server: Optional[str] = Field("localhost")
    password: Optional[SecretStr] = Field(None)
    port: int = Field(5432)
    options: EngineOptions = EngineOptions()  # type: ignore

    @property
    def url(self) -> SecretStr:
        """Return SQLAlchemy database URL."""
        pwd = str(self.password.get_secret_value()) if self.password else ""
        return SecretStr(
            "".join(
                [
                    f"{self.engine}://",
                    f"{self.user}:{pwd}",
                    f"@{self.server}:{self.port}",
                    f"/{self.database}",
                ]
            )
        )


class Settings(BaseSettings):
    """App settings."""

    version: str = Field(__VERSION__, description="App version number")

    db: AppDatabase = AppDatabase()  # type: ignore
    backend_cors_origins: Tuple[str, ...] = Field(default=("*",))

    env: AppEnvEnum = Field(..., description="App environment")
    log_level: LogLevel = Field(LogLevel.INFO, description="Python logging module log level")

    class Config:  # noqa
        """Pydantic config."""

        # Prefix for environment variables
        env_prefix = "APP_"
        env_file = ".env"
        # environment variables for fields are case insensitive
        case_sensitive = False
        # nested model env variables use {field_name}__{submodel_field_name}
        env_nested_delimiter = "__"
        # if settings are frozen, then they are hashable and can be cached.
        allow_mutation = False
        frozen = True


@lru_cache()
def get_settings() -> Settings:
    """Return the app settings object."""
    # This allows specifying the source of environment variables via an env file
    # See https://pydantic-docs.helpmanual.io/usage/settings/#dotenv-env-support
    return Settings()  # type: ignore
