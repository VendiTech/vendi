DOCKER_PATH ?= vendi-docker/docker-compose.yml
CONSUMER_PATH ?= vendi-docker/consumers.yml
TEST_PATH ?= vendi-docker/test.yml
ALEMBIC_INI_PATH ?= mspy_vendi/db/migrations/alembic.ini

SERVICE_NAME ?= vendi-service
SERVICE_DB ?= vendi-db
CONSUMER_NAYAX ?= nayax-consumer
CONSUMER_DATAJAM ?= datajam-consumer

.PHONY:  help build up down ruff-fix lint inside-container up-test migration upgrade-version downgrade-version up-db


help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile \
	| awk 'BEGIN{FS=":.*## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

ruff-fix: ## Runs ruff fix
	ruff check . --fix

format: ## Runs the format command
	ruff format .

lint: format ruff-fix  ## Run linters
	pre-commit run --all-files

up:  ## Up FastAPI service, scheduler and consumers
	docker compose -f ${DOCKER_PATH} up --remove-orphans

down: ## Down FastAPI service, scheduler and consumers
	docker compose -f ${DOCKER_PATH} down --remove-orphans

up-nayax-consumer: ## Up Nayax consumer
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} up ${CONSUMER_NAYAX} --remove-orphans

up-datajam-consumer: ## Up Datajam consumer
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} up ${CONSUMER_DATAJAM} --remove-orphans

up-consumers: ## Up all consumers
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} up ${CONSUMER_DATAJAM} ${CONSUMER_NAYAX} --remove-orphans

build: ## Build the docker image
	docker compose -f ${DOCKER_PATH} build

build-consumer: ## Build the docker image for consumers
	docker compose -f ${DOCKER_PATH} -f ${CONSUMER_PATH} build

up-test: ## Up Tests
	docker compose -f ${DOCKER_PATH} -f ${TEST_PATH} up ${SERVICE_NAME} --remove-orphans --exit-code-from ${SERVICE_NAME}

migration: ## Create a new migration
	docker compose -f ${DOCKER_PATH} run ${SERVICE_NAME} alembic -c ${ALEMBIC_INI_PATH} revision --autogenerate -m "$(m)"

upgrade-version: ## Upgrade to a specific version
	docker compose -f ${DOCKER_PATH} run ${SERVICE_NAME} alembic -c ${ALEMBIC_INI_PATH} upgrade $(if $(v),$(v),head)

downgrade-version: ## Downgrade to a specific version
	docker compose -f ${DOCKER_PATH} run ${SERVICE_NAME} alembic -c ${ALEMBIC_INI_PATH} downgrade ${n}

up-db: ## Up database
	docker compose -f ${DOCKER_PATH} up ${SERVICE_DB} --remove-orphans
