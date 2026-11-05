FROM python:3.14-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV ENVIRONMENT=production \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock .python-version /app/
RUN uv sync --locked --no-dev --no-install-project

COPY ./ /app/
RUN uv sync --locked --no-dev

# Secrets come from env_file at runtime; session + config live in the /app/data volume.
ENTRYPOINT ["/app/.venv/bin/python", "main/main.py"]
