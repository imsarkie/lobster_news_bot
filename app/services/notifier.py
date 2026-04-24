import logging
from html import escape

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


def _build_message(story: dict) -> str:
    title = escape(story.get("title", "No title"))
    score = story.get("score", 0)
    short_id = story.get("short_id", "")
    comments_url = story.get("comments_url") or f"https://lobste.rs/s/{short_id}"
    # Self-posts have no external URL; fall back to the comments page.
    url = story.get("url") or comments_url

    tags = story.get("tags") or []
    tags_line = ("  ".join(f"#{escape(t)}" for t in tags) + "\n") if tags else ""

    return (
        f"<b>{title}</b> (⭐ Score: {score})\n\n"
        f"<b>Link:</b> {url}\n"
        f"<b>Comments:</b> {comments_url}\n"
        f"<b>Tags:</b> {tags_line}\n"
    )


def _build_inline_keyboard(story: dict) -> dict:
    short_id = story.get("short_id", "")
    comments_url = story.get("comments_url") or f"https://lobste.rs/s/{short_id}"
    url = story.get("url") or comments_url
    comment_count = story.get("comment_count", 0)
    comments_label = f" {comment_count} Comments"

    return {
        "inline_keyboard": [
            [
                {"text": "Read", "url": url},
                {"text": comments_label, "url": comments_url},
            ]
        ]
    }


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True,
)
async def send_story(story: dict) -> None:
    """Send a single story to the configured Telegram chat."""
    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": _build_message(story),
        "parse_mode": "HTML",
        "reply_markup": _build_inline_keyboard(story),
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(api_url, json=payload)
        if not response.is_success:
            logger.error(
                "Telegram API error for story %s: %s %s",
                story.get("short_id"),
                response.status_code,
                response.text,
            )
            response.raise_for_status()

    logger.info("Sent story %s to Telegram", story.get("short_id"))
