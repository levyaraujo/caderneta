FROM public.ecr.aws/docker/library/python:3.12-slim-bullseye AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.in-project true \
    && poetry install --no-interaction --no-root --only main

COPY . .

FROM public.ecr.aws/docker/library/python:3.12-slim-bullseye

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app .

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["fastapi", "run"]
