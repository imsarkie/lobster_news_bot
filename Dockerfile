# ── Build stage ──────────────────────────────────────────────────────────────
FROM python:3.14-slim AS builder

WORKDIR /app

# Install uv (fast Python package manager)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency manifest (and lock file when present for reproducible builds)
COPY pyproject.toml uv.lock* ./

# Install production dependencies into the project-local virtualenv
RUN uv sync --no-dev

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.14-slim

WORKDIR /app

# Re-install uv so we can use `uv run` at runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy the virtualenv and project files from the build stage
COPY --from=builder /app /app

# Copy application source
COPY . .

EXPOSE 8000

# Run Alembic migrations then start the server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
