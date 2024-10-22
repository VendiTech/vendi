DOCKER_PATH ?= vendi-docker/docker-compose.yml

SERVICE_NAME ?= vendi-service
SERVICE_DB ?= vendi-db

ruff-fix:
	ruff check . --fix

format:
	ruff format .

lint: format ruff-fix
	pre-commit run --all-files

up:
	docker compose -f ${DOCKER_PATH} up --remove-orphans

build:
	docker compose -f ${DOCKER_PATH} build
