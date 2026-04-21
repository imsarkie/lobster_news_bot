import logging

from app.config import settings

logger = logging.getLogger(__name__)


def filter_stories(stories: list[dict], threshold: int | None = None) -> list[dict]:
    """Return only stories whose score meets the minimum threshold."""
    min_score = threshold if threshold is not None else settings.score_threshold
    filtered = [s for s in stories if s.get("score", 0) >= min_score]
    logger.info(
        "Filtered %d/%d stories with score >= %d",
        len(filtered),
        len(stories),
        min_score,
    )
    return filtered
