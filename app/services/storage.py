import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SentStory

logger = logging.getLogger(__name__)


async def is_story_sent(session: AsyncSession, story_id: str) -> bool:
    """Return True if the story_id has already been sent."""
    result = await session.execute(
        select(SentStory.id).where(SentStory.story_id == story_id)
    )
    return result.scalar_one_or_none() is not None


async def mark_story_sent(session: AsyncSession, story: dict) -> None:
    """Persist a sent story record to prevent future duplicate sends."""
    record = SentStory(
        story_id=story["short_id"],
        title=story.get("title", ""),
        url=story.get("url") or story.get("comments_url", ""),
    )
    session.add(record)
    await session.commit()
    logger.info("Marked story %s as sent", story["short_id"])
