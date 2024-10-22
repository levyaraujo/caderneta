test-env:
	docker compose -f tests/docker-compose.yml up

test:
	ENV=testing poetry run pytest tests -vv

ruff-fix:
	poetry run ruff format && poetry run ruff check --config ruff.toml --fix

cli:
	PYTHONPATH=$(PWD) poetry run typer cli.py run
