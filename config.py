import json
import os
from pathlib import Path
import secrets
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache
from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, validator


class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
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

    DB: str = "cloudant"
    DETA_BASE_KEY: Optional[str]
    CLOUDANT_AUTH_TYPE: Optional[str] = "IAM"
    CLOUDANT_URL: Optional[HttpUrl] = "https://bluemix.cloudantnosqldb.appdomain.cloud/"
    CLOUDANT_APIKEY: Optional[str] = ""

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAILS_ENABLED: bool = False
    USERS_OPEN_REGISTRATION: bool = False

    # Extras

    class Config:
        case_sensitive = True
        extra = 'ignore'


@lru_cache()
def get_settings():
    file = Path('settings.json').absolute()
    if not file.exists():
        print(f'WARNING: {file} file not found. Switching to Env Variables for config.')
        return Settings(**os.environ)
        # raise Exception('Key file is missing.')
    with open('settings.json') as fin:
        keys = json.load(fin)

    return Settings(**keys)


settings = get_settings()
