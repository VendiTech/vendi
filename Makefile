DOCKER_PATH ?= vendi-docker/docker-compose.yml
CONSUMER_PATH ?= vendi-docker/consumers.yml
TEST_PATH ?= vendi-docker/test.yml
ALEMBIC_INI_PATH ?= mspy_vendi/db/migrations/alembic.ini

SERVICE_NAME ?= vendi-service
SERVICE_DB ?= vendi-db
CONSUMER_NAYAX ?= nayax-consumer
CONSUMER_DATAJAM ?= datajam-consumer

ruff-fix:
	ruff check . --fix

format:
	ruff format .

lint: format ruff-fix
	pre-commit run --all-files

up:
	docker compose -f ${DOCKER_PATH} up --remove-orphans

up-nayax-consumer:
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} up ${CONSUMER_NAYAX} --remove-orphans

up-datajam-consumer:
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} up ${CONSUMER_DATAJAM} --remove-orphans

up-consumers:
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} up ${CONSUMER_DATAJAM} ${CONSUMER_NAYAX} --remove-orphans

build:
	docker compose -f ${DOCKER_PATH} build

build-consumer:
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} build

up-test:
	docker compose -f ${DOCKER_PATH} -f ${TEST_PATH} up ${SERVICE_NAME} --remove-orphans --exit-code-from ${SERVICE_NAME}

migration:
	docker compose -f ${DOCKER_PATH} run ${SERVICE_NAME} alembic -c ${ALEMBIC_INI_PATH} revision --autogenerate -m "$(m)"

upgrade-version:
	docker compose -f ${DOCKER_PATH} run ${SERVICE_NAME} alembic -c ${ALEMBIC_INI_PATH} upgrade $(if $(v),$(v),head)

downgrade-version:
	docker compose -f ${DOCKER_PATH} run ${SERVICE_NAME} alembic -c ${ALEMBIC_INI_PATH} downgrade ${n}

up-db:
	docker compose -f ${DOCKER_PATH} up ${SERVICE_DB} --remove-orphans
