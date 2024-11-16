FROM python:3.12.6-slim-bullseye

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root --no-ansi --only main

COPY . .

<<<<<<< Updated upstream
RUN chmod +x /entrypoint.sh

EXPOSE 8000

CMD ["fastapi", "run"]
=======
FROM --platform=$BUILDPLATFORM python:3.12.6-slim-bullseye

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app .

ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["fastapi", "run"]
>>>>>>> Stashed changes
