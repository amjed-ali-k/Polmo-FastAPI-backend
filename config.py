import json
import os
from pathlib import Path
import secrets
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache
from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, validator


class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SERVER_NAME: str = ""
    SERVER_HOST: AnyHttpUrl = "http://127.0.0.1"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = ""
    SENTRY_DSN: Optional[HttpUrl] = ""

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    DETA_BASE_KEY: Optional[str] = "a0di4a85_n2bLfgFjWoC11bxkTzNwu443GGcAdMeJ"

    # Extras

    class Config:
        case_sensitive = True
        extra = 'ignore'


@lru_cache()
def get_settings():
    return Settings(**os.environ)


settings = get_settings()
