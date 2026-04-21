import logging

from app.database import AsyncSessionLocal
from app.services.filter import filter_stories
from app.services.lobsters import fetch_hottest_stories
from app.services.notifier import send_story
from app.services.storage import is_story_sent, mark_story_sent

logger = logging.getLogger(__name__)


async def run_job() -> dict:
    """
    Main scheduled job:
    1. Fetch hottest Lobsters stories.
    2. Filter by score threshold.
    3. Skip already-sent stories.
    4. Send new stories to Telegram and record them in the DB.
    """
    logger.info("Lobsters job started")
    stats = {"fetched": 0, "filtered": 0, "sent": 0, "skipped": 0, "errors": 0}

    try:
        stories = await fetch_hottest_stories()
        stats["fetched"] = len(stories)

        filtered = filter_stories(stories)
        stats["filtered"] = len(filtered)

        async with AsyncSessionLocal() as session:
            for story in filtered:
                story_id: str | None = story.get("short_id")
                if not story_id:
                    logger.warning("Story missing short_id, skipping: %s", story)
                    continue

                try:
                    if await is_story_sent(session, story_id):
                        logger.debug("Story %s already sent, skipping", story_id)
                        stats["skipped"] += 1
                        continue

                    await send_story(story)
                    await mark_story_sent(session, story)
                    stats["sent"] += 1

                except Exception as exc:
                    logger.error("Error processing story %s: %s", story_id, exc, exc_info=True)
                    stats["errors"] += 1

    except Exception as exc:
        logger.error("Job failed with an unrecoverable error: %s", exc, exc_info=True)
        raise

    logger.info("Lobsters job finished: %s", stats)
    return stats
