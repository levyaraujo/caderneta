test-env:
	docker compose -f tests/docker-compose.yml up

test:
	poetry run pytest tests -vv

ruff-fix:
	poetry run ruff format && ruff check --config ruff.toml --fix