import logging

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

HOTTEST_URL = "https://lobste.rs/hottest.json"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(httpx.HTTPError),
    reraise=True,
)
async def fetch_hottest_stories() -> list[dict]:
    """Fetch the hottest stories from the Lobsters API."""
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(HOTTEST_URL)
        response.raise_for_status()
        stories: list[dict] = response.json()
        logger.info("Fetched %d stories from Lobsters", len(stories))
        return stories
