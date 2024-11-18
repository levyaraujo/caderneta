FROM public.ecr.aws/docker/library/python:3.12-slim-bullseye AS base

WORKDIR /app

ENV POETRY_HOME='/usr/local' \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -

FROM base AS builder

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main

COPY . .

FROM base AS final

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app .

EXPOSE 8000

CMD ["fastapi", "run"]
