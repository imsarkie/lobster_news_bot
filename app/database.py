import asyncio
import logging
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def ensure_database_exists(max_retries: int = 10, delay: float = 3.0) -> None:
    """Connect to MySQL without a database and create the app DB if it is missing."""
    no_db_url = (
        f"mysql+aiomysql://{settings.mysql_user}:{quote_plus(settings.mysql_password)}"
        f"@{settings.mysql_host}:{settings.mysql_port}/"
    )
    tmp_engine = create_async_engine(no_db_url, echo=False)
    try:
        for attempt in range(1, max_retries + 1):
            try:
                async with tmp_engine.connect() as conn:
                    await conn.execute(
                        text(
                            f"CREATE DATABASE IF NOT EXISTS `{settings.mysql_db}` "
                            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                        )
                    )
                logger.info("Database '%s' is ready.", settings.mysql_db)
                return
            except Exception as exc:
                if attempt < max_retries:
                    logger.warning(
                        "MySQL not ready (attempt %d/%d): %s. Retrying in %.0fs\u2026",
                        attempt,
                        max_retries,
                        exc,
                        delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error("Could not ensure database after %d attempts.", max_retries)
                    raise
    finally:
        await tmp_engine.dispose()


async def wait_for_db(max_retries: int = 10, delay: float = 3.0) -> None:
    """Retry database connection until it succeeds or max_retries is reached."""
    for attempt in range(1, max_retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection established")
            return
        except Exception as exc:
            if attempt < max_retries:
                logger.warning(
                    "Database not ready (attempt %d/%d): %s. Retrying in %.0fs…",
                    attempt,
                    max_retries,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
            else:
                logger.error("Database connection failed after %d attempts.", max_retries)
                raise
