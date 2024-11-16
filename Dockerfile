FROM --platform=$BUILDPLATFORM python:3.12.6-slim-bullseye AS builder

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root --no-ansi --only main

FROM --platform=$TARGETPLATFORM python:3.12.6-slim-bullseye

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

ENV PATH=/usr/local/lib/python3.12/site-packages:$PATH
ENV PATH=/usr/local/bin:$PATH

COPY . .

EXPOSE 8000

CMD ["fastapi", "run"]
