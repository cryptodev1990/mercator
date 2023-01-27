"""App settings and configuration management."""
import os
from functools import lru_cache
from typing import Any, Dict, Optional

# pylint: disable=no-name-in-module
from pydantic import (
    BaseSettings,
    Field,
    root_validator,
)

from api.core.logging import get_logger

__VERSION__ = "0.0.1"

logger = get_logger(__name__)


class Settings(BaseSettings):
    """Config settings."""

    app_name: str = Field("dubo_api", env="APP_NAME")
    version: str = Field(__VERSION__)
    app_env: str = Field("dev", env="APP_ENV")

    # OpenAI config
    openai_key: str = Field(..., env="OPENAI_KEY")

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

    worker_id_length: int = Field(
        8, describe="Length of the generated random worker ID", env_var="WORKER_ID_LENGTH"
    )



@lru_cache()
def get_settings() -> Settings:
    """Return the app settings object."""
    # This allows specifying the source of environment variables via an env file
    # See https://pydantic-docs.helpmanual.io/usage/settings/#dotenv-env-support
    env_file: Optional[str] = os.environ.get("ENV_FILE", ".env")
    if env_file and os.path.isfile(env_file):
        return Settings(_env_file=env_file)  # type: ignore
    return Settings()  # type: ignore
