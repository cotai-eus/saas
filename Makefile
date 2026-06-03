.PHONY: setup up down logs clean migrate-init migrate-up migrate-down

setup:
	./setup.sh

up:
	docker network create proxy || true
	docker compose -f infra/docker-compose.yml --env-file infra/.env up -d --build

down:
	docker compose -f infra/docker-compose.yml --env-file infra/.env down

logs:
	docker compose -f infra/docker-compose.yml --env-file infra/.env logs -f

clean:
	docker compose -f infra/docker-compose.yml --env-file infra/.env down -v
	rm -rf infra/traefik/certs/*

# Database migrations
migrate-init:
	cd backend && alembic revision --autogenerate -m "Initial schema"

migrate-up:
	cd backend && alembic upgrade head

migrate-down:
	cd backend && alembic downgrade -1
