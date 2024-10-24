DOCKER_PATH ?= vendi-docker/docker-compose.yml
CONSUMER_PATH ?= vendi-docker/consumers.yml

SERVICE_NAME ?= vendi-service
SERVICE_DB ?= vendi-db
CONSUMER_NAYAX ?= nayax-consumer

ruff-fix:
	ruff check . --fix

format:
	ruff format .

lint: format ruff-fix
	pre-commit run --all-files

up:
	docker compose -f ${DOCKER_PATH} up --remove-orphans

up-consumer:
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} up ${CONSUMER_NAYAX} --remove-orphans

build:
	docker compose -f ${DOCKER_PATH} build

build-consumer:
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} build
