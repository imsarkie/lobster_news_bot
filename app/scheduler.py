import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def setup_scheduler() -> None:
    """Register the Lobsters fetch job on a 10-minute interval."""
    # Import here to avoid circular imports at module load time.
    from app.worker import run_job

    scheduler.add_job(
        run_job,
        trigger=IntervalTrigger(minutes=10),
        id="lobsters_fetch_job",
        name="Fetch and notify Lobsters stories",
        replace_existing=True,
        misfire_grace_time=60,
    )
    logger.info("Scheduler configured: lobsters_fetch_job every 10 minutes")
