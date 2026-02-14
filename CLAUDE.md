# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kitsune is a PydanticAI-based agent served as a web app. It uses the OpenRouter `moonshotai/kimi-k2.5` model, instrumented with Logfire for observability, and served via Uvicorn on port 8010.

## Tech Stack

- Python 3.14, managed with **uv**
- **PydanticAI** for agent framework ([Documentation](https://ai.pydantic.dev/llms.txt))
- **Pydantic** for validation ([Documentation](https://docs.pydantic.dev/latest/llms.txt))
- **Logfire** for tracing/observability
- **Uvicorn** as ASGI server

## Commands

```bash
uv sync              # Install dependencies
uv run main.py       # Run the web app (localhost:8010, auto-reload)
```

## Structure

- `main.py` — App entrypoint: agent definition, Logfire setup, Uvicorn server
- `kitsune/` — Package directory (currently empty)
- `pyproject.toml` — Project config and dependencies
