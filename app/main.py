import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine, ensure_database_exists, wait_for_db
from app.scheduler import scheduler, setup_scheduler
from app.worker import run_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("Starting up Lobster Bot…")

    # Ensure the database exists (creates it if missing) before connecting.
    await ensure_database_exists()

    # Wait for MySQL to be reachable (important in Docker Compose environments).
    await wait_for_db()

    # Auto-create tables that don't exist yet.
    # For schema changes, use `alembic upgrade head` instead.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema verified")

    setup_scheduler()
    scheduler.start()
    logger.info("Background scheduler started")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
    await engine.dispose()
    logger.info("Database engine disposed")


app = FastAPI(
    title="Lobster Bot",
    description="Telegram notification bot for Lobsters (lobste.rs)",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["ops"])
async def health():
    """Return the current service status."""
    return {
        "status": "ok",
        "scheduler_running": scheduler.running,
    }


@app.post("/trigger", tags=["ops"])
async def trigger():
    """Manually trigger a fetch-and-notify run."""
    logger.info("Manual trigger received via POST /trigger")
    stats = await run_job()
    return {"status": "ok", "stats": stats}
