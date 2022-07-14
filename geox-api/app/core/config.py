import hashlib
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union



from pydantic import (AnyHttpUrl, BaseSettings, EmailStr, Field, PostgresDsn,
                      validator)


class Settings(BaseSettings):
    """Settings for the """
    # For JWT
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_MACHINE_CLIENT_ID: str
    AUTH0_MACHINE_CLIENT_SECRET: str
    AUTH0_DOMAIN: str
    AUTH0_API_AUDIENCE: str
    # TODO: AUTH0_ALGORITHMS should be an enum/literal set
    AUTH0_ALGORITHMS: str = Field("RS256")
    APP_SECRET_KEY: str

    ## TODO: are these used in the backend?
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    FRONTEND_URL: AnyHttpUrl = Field(..., description="URL that the frontend uses.")
    POSTGRES_CONNECTION: PostgresDsn

    class Config: # noqa
        env_file = '.env'
        case_sensitive = True

@lru_cache()
def _get_settings(env_file: Optional[str], env_file_hash: str) -> Settings:
    return Settings(_env_file=env_file)

def get_settings() -> Settings:
    """Return the app settings object."""
    # This allows specifying the source of environment variables via an env file
    # See https://pydantic-docs.helpmanual.io/usage/settings/#dotenv-env-support
    env_file: Optional[str] = os.environ.get('ENV_FILE', '.env')
    if env_file and os.path.isfile(env_file):
        env_file_hash = hashlib.md5(open(env_file,'rb').read()) if os.path.isfile(env_file) else ''
    else:
        env_file_hash = ''
        env_file = None
    # Using an inner function will cache on the *contents* of the settings file,
    # so it will update if that changes. This may be unnecessary - but I think it makes sense.
    return _get_settings(env_file, env_file_hash)
