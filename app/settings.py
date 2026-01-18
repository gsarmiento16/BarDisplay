from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    MONGO_URI: str
    MONGO_DB_NAME: str
    EMT_BASE_URL: str
    EMT_ACCESS_TOKEN: str
    EMT_TIMEOUT_SECONDS: int = 10

    DEFAULT_REFRESH_SECONDS: int = 60
    DEFAULT_SWAP_SECONDS: int = 30
    DEFAULT_LAYOUT: str = "horizontal"
    DEFAULT_THEME: str = "purple"
    DEFAULT_BOARD_HEADER_TEXT: str = "Bus arriving at nearby stops"

    ADMIN_SECRET: str = "change-me"

    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_WEBHOOK_SECRET: str | None = None
    TELEGRAM_ALLOWED_UPDATE_TYPES: str = "message,edited_message"
    TELEGRAM_MAX_IMAGE_MB: int = 5
    TELEGRAM_UPLOADS_DIR: str = "./uploads"
    TELEGRAM_MODE: str = "webhook"
