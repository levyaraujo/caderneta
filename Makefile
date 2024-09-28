test-env:
	docker compose -f tests/docker-compose.yml up

test:
	pytest tests -vv -s

ruff-fix:
	ruff format && ruff check --config ruff.toml --fix