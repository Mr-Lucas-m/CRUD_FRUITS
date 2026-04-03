from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    APP_ENV: str
    APP_TITLE: str
    APP_VERSION: str
    APP_DEBUG: bool
    DEFAULT_PAGE_SIZE: int
    MAX_PAGE_SIZE: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()