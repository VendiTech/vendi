DOCKER_PATH ?= vendi-docker/docker-compose.yml
CONSUMER_PATH ?= vendi-docker/consumers.yml
TEST_PATH ?= vendi-docker/test.yml

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

up-test:
	docker compose -f ${DOCKER_PATH} -f ${TEST_PATH} up ${SERVICE_NAME} --remove-orphans --exit-code-from ${SERVICE_NAME}

makemigrations:
	docker compose -f ${DOCKER_PATH} run ${SERVICE_NAME} python3 manage.py makemigrations

migrate:
	docker compose -f ${DOCKER_PATH} run ${SERVICE_NAME} python3 manage.py migrate ${m}

create_superuser:
	docker compose -f ${DOCKER_PATH} run ${SERVICE_NAME} python3 manage.py createsuperuser
