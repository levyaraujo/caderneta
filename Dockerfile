FROM python:3.12.6-alpine3.20

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . .

EXPOSE 8000

CMD ["fastapi", "run"]