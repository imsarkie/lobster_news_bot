# Lobster Bot

A Telegram notification bot that monitors [Lobste.rs](https://lobste.rs) and pushes high-scoring stories straight to a Telegram chat. It polls the Lobsters hottest-stories API every 10 minutes, filters out anything below a configurable score threshold, and sends each new story once — with inline "Read" and "Comments" buttons.

---

## How it works

1. **Fetch** — Every 10 minutes the scheduler calls the `lobste.rs/hottest.json` endpoint.
2. **Filter** — Stories are kept only if their score is ≥ `SCORE_THRESHOLD` (default `15`).
3. **Deduplicate** — Already-sent story IDs are stored in MySQL; duplicates are skipped.
4. **Notify** — Each new story is sent to the configured Telegram chat as an HTML-formatted message with inline buttons.

A FastAPI app wraps the scheduler and exposes two utility endpoints:
- `GET /health` — liveness check.
- `POST /trigger` — manually run the fetch-and-notify cycle.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- A Telegram bot token — create one via [@BotFather](https://t.me/BotFather)
- The chat ID of the channel/group/user you want to post to

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/imsarkie/lobster_news_bot.git
cd lobster_news_bot
```

### 2. Create the `.env` file

Copy the example below and fill in your values:

```env
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHAT_ID=-1001234567890

# Score filter (optional, default is 15)
SCORE_THRESHOLD=15

# MySQL
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=lobster
MYSQL_PASSWORD=your_secure_password
MYSQL_DB=lobster_bot
MYSQL_ROOT_PASSWORD=your_root_password
```

> **Tip:** `MYSQL_HOST` must be `db` when running with Docker Compose (that is the service name). Change it to `localhost` only if you run MySQL separately.

### 3. Start the stack

```bash
docker compose up -d
```

Docker Compose will:
- Pull and start a **MySQL 8.0** container.
- Build the **app** image.
- Wait for MySQL to be healthy before starting the app.
- Auto-create the database schema on first boot.

### 4. Verify it's running

```bash
curl http://localhost:8000/health
# {"status":"ok","scheduler_running":true}
```

---

## Running locally (without Docker)

Requires **Python ≥ 3.14** and a running MySQL instance.

```bash
# Install uv (fast package manager used by this project)
pip install uv

# Install dependencies
uv sync

# Set environment variables (or create a .env file as shown above,
# with MYSQL_HOST=localhost)

# Run database migrations
uv run alembic upgrade head

# Start the app
uv run uvicorn app.main:app --reload
```

---

## Configuration reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Yes | — | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Yes | — | Target chat / channel ID |
| `SCORE_THRESHOLD` | No | `15` | Minimum Lobsters score to notify |
| `MYSQL_HOST` | No | `localhost` | MySQL hostname |
| `MYSQL_PORT` | No | `3306` | MySQL port |
| `MYSQL_USER` | No | `lobster` | MySQL username |
| `MYSQL_PASSWORD` | Yes | — | MySQL password |
| `MYSQL_DB` | No | `lobster_bot` | MySQL database name |
| `MYSQL_ROOT_PASSWORD` | Yes (Docker) | — | MySQL root password (Compose only) |

---

## Useful commands

```bash
# View logs
docker compose logs -f app

# Manually trigger a fetch
curl -X POST http://localhost:8000/trigger

# Stop the stack
docker compose down

# Stop and remove volumes (wipes the database)
docker compose down -v
```

---

## Project structure

```
app/
  config.py          # Settings loaded from .env
  database.py        # SQLAlchemy async engine + session
  main.py            # FastAPI app & lifespan (startup/shutdown)
  models.py          # ORM models
  scheduler.py       # APScheduler setup (10-minute interval)
  worker.py          # Core fetch → filter → send pipeline
  services/
    lobsters.py      # Fetches hottest.json from lobste.rs
    filter.py        # Score threshold filtering
    notifier.py      # Sends stories to Telegram
    storage.py       # Tracks sent story IDs in MySQL
alembic/             # Database migrations
docker-compose.yml
Dockerfile
pyproject.toml
```
