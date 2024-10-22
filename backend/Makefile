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

deploy_heroku:
	heroku container:login
	docker build -t registry.heroku.com/vendi-backend-stg/web1 -f vendi-docker/Dockerfile --target prod .
	docker push registry.heroku.com/vendi-backend-stg/web1 || true
	heroku container:release -a vendi-backend-stg web1
