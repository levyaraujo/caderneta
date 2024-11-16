FROM --platform=$BUILDPLATFORM python:3.12.6-slim-bullseye AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.9.0

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true

RUN poetry install --no-interaction --no-root --only main

COPY . .

RUN poetry install --no-interaction

FROM --platform=$TARGETPLATFORM python:3.12.6-slim-bullseye

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app .

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]