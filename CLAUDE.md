# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kitsune is an AI agent microservice. FastAPI backend with PydanticAI agent (AG-UI protocol) and per-user Docker-sandboxed marimo notebooks. Served via Uvicorn on port 8010.

## Tech Stack

- Python 3.14, managed with **uv**
- **FastAPI** as web framework
- **PydanticAI** + **AG-UI** for agent protocol ([Documentation](https://ai.pydantic.dev/llms.txt))
- **Marimo** for interactive notebooks (edit mode, per-user Docker containers)
- **Docker** SDK for Python — sandbox container lifecycle
- **Logfire** for tracing/observability

## Commands

```bash
uv sync                                          # Install Python dependencies
uv run main.py                                   # Run FastAPI on localhost:8010 (auto-reload)
docker build -t kitsune-marimo-sandbox docker/marimo/   # Build sandbox image
```

## Structure

```
main.py                         # FastAPI app: AG-UI endpoint, sandbox lifecycle, health check
pyproject.toml                  # Python deps (fastapi, pydantic-ai, docker)
docker/marimo/Dockerfile        # Sandbox image: python:3.14-slim + marimo + data science deps
kitsune/
├── config.py                   # Environment config (incl. sandbox settings)
├── models.py                   # Pydantic models (User, Message, Session)
├── utils.py                    # Utility functions
├── logging.py                  # JSON rotating file logger
├── agents/
│   └── marimo.py               # Marimo agent: deps, notebook tools, cell builder
└── services/
    └── sandbox.py              # SandboxManager: Docker container lifecycle per session
notebooks/                      # Template marimo .py notebooks (seeded into user dirs)
data/notebooks/{session_id}/    # Per-user notebook storage (gitignored)
```

## Architecture

- **AG-UI protocol**: Backend uses `AGUIAdapter.dispatch_request()` — zero custom SSE code
- Any AG-UI compatible frontend can consume the `/ag-ui` endpoint
- **Sandbox isolation**: Each user session gets a dedicated Docker container running `marimo edit` on port 2718 (mapped to host port 9100–9200)
- `GET /notebooks/{session_id}` — returns marimo edit URL for iframe embedding
- `SandboxManager` handles container create/destroy, port allocation, and stale cleanup (30 min timeout)
- Session ID passed via `x-session-id` header (auth TBD)
- **Health check**: `GET /health` for container orchestration
