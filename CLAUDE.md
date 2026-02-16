# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kitsune is an AI agent microservice. FastAPI backend with PydanticAI agent (AG-UI protocol) and marimo notebooks. Served via Uvicorn on port 8010.

## Tech Stack

- Python 3.14, managed with **uv**
- **FastAPI** as web framework
- **PydanticAI** + **AG-UI** for agent protocol ([Documentation](https://ai.pydantic.dev/llms.txt))
- **Marimo** for interactive notebooks (run mode)
- **Logfire** for tracing/observability

## Commands

```bash
uv sync              # Install Python dependencies
uv run main.py       # Run FastAPI on localhost:8010 (auto-reload)
```

## Structure

```
main.py                         # FastAPI app: AG-UI endpoint, marimo mount, health check
pyproject.toml                  # Python deps (fastapi, pydantic-ai-slim[ag-ui], marimo)
kitsune/
├── config.py                   # Environment config
├── models.py                   # Pydantic models (User, Message, Session)
├── utils.py                    # Utility functions
└── logging.py                  # JSON rotating file logger
notebooks/                      # Marimo .py notebook files (mounted at /notebooks/*)
```

## Architecture

- **AG-UI protocol**: Backend uses `AGUIAdapter.dispatch_request()` — zero custom SSE code
- Any AG-UI compatible frontend can consume the `/api/ag-ui` endpoint
- **Health check**: `GET /health` for container orchestration
