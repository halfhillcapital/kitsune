# Stage 1: Build frontend
FROM node:22-slim AS frontend
WORKDIR /app
COPY frontend/package*.json frontend/
RUN cd frontend && npm ci
COPY frontend/ frontend/
RUN cd frontend && npm run build
# outDir is ../static (relative to frontend/), so output lands at /app/static

# Stage 2: Kitsune server
FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Install Python deps (cached unless lockfile changes)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .
COPY --from=frontend /app/static ./static

RUN mkdir -p data/notebooks

EXPOSE 8010

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
