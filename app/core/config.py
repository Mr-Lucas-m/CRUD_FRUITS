from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    APP_ENV: str
    APP_TITLE: str
    APP_VERSION: str
    APP_DEBUG: bool
    DEFAULT_PAGE_SIZE: int
    MAX_PAGE_SIZE: int

    # Auth JWT
    SECRET_KEY: str = "dev-secret-key-insecure-change-in-production-32c"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
