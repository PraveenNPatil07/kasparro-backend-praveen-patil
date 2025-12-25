.PHONY: up down restart build test logs ps migrate etl

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

build:
	docker-compose build

test:
	docker-compose run --rm api pytest

logs:
	docker-compose logs -f

ps:
	docker-compose ps

migrate:
	docker-compose run --rm api alembic upgrade head

etl:
	docker-compose run --rm etl python -m app.ingestion.runner
