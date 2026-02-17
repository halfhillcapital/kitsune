FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

RUN uv pip install --system \
    marimo \
    numpy \
    pandas \
    polars \
    matplotlib \
    seaborn \
    plotly \
    scikit-learn \
    scipy

RUN mkdir -p /notebooks

EXPOSE 2718

CMD ["marimo", "edit", "--host", "0.0.0.0", "--port", "2718", "--headless", "--no-token", "/notebooks"]
