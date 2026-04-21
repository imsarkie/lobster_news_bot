from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    telegram_bot_token: str
    telegram_chat_id: str
    score_threshold: int = 15

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "lobster"
    mysql_password: str
    mysql_db: str = "lobster_bot"

    @property
    def database_url(self) -> str:
        """Async URL used by the application (aiomysql driver)."""
        return (
            f"mysql+aiomysql://{self.mysql_user}:{quote_plus(self.mysql_password)}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """Sync URL used by Alembic migrations (pymysql driver)."""
        return (
            f"mysql+pymysql://{self.mysql_user}:{quote_plus(self.mysql_password)}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
