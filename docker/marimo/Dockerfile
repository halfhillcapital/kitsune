FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN uv pip install --system \
    pydantic-ai \
    openai \
    mcp \
    marimo \
    numpy \
    pandas \
    polars \
    matplotlib \
    seaborn \
    plotly \
    altair \
    scikit-learn \
    scipy \
    duckdb \
    sqlglot \
    ruff \
    python-lsp-server \
    python-lsp-ruff \
    websockets

RUN mkdir -p /notebooks /root/.config/marimo

COPY docker/marimo/marimo.toml /root/.config/marimo/marimo.toml

WORKDIR /notebooks

EXPOSE 2718

CMD ["marimo", "edit", "--host", "0.0.0.0", "--port", "2718", "--headless", "--no-token", "/notebooks"]
