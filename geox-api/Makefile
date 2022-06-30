# Makefile to build and run Mercator GeoX app
#
# This is a self-documenting makefile. See
# Self documenting makefile https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

SHELL := bash
.DEFAULT_GOAL := help

PSQL_BIN ?= psql

.PHONY: help
help:  ## Display available tasks
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: docker-build
docker-build: setup ## Build docker container
	DOCKER_BUILDKIT=0 docker build . -t geox-web:latest


.PHONY: docker-run
docker-run: docker-build ## Run docker container
	# Run the production container
	docker run -p 8080:8080 --env-file .env.docker geox-web:latest

.PHONY: docker-connect
docker-connect: ## Connect to local docker
	docker run -it geox-web:latest bash

.PHONY: setup
setup: ## Set up for local development
	python3 -m venv env; \
	pip install -r requirements.txt; \
	pip install -r requirements-dev.txt; \
	test `command -v docker` || (echo "\033[31m Please install docker" && exit -1); \


.PHONY: build
build: setup ## Build app for local development
	pip install -r requirements.txt; \
	pip install -r requirements-dev.txt; \
        cd py-geolift; \
	Rscript --verbose dependencies.R; \
	poetry config virtualenvs.create false; \
    	poetry build; \
    	pip install dist/pygeolift-*.tar.gz; \
	cd ..; \
	brew install overmind

.PHONY: dev
dev:  ## Run app locally
	export $$(cat .env.local | xargs) && overmind start

.PHONY: lint
lint: ## Lint the project
	# Lint the project
	black .

.PHONY: deploy
deploy: ## Deploy the project to flyctl
	test `command -v flyctl` || (echo "\033[31m Please install flyctl from fly.io" && exit -1);
	flyctl deploy

.PHONY: test
test: ## Run tests
	export $$(cat .env.local | xargs) && pytest -x -vvv .

.PHONY: db-revision
db-revision: ## Revise database with alembic
	# alembic revision -m "$(msg)"
	# TODO how should this actually be done?
	# export $(cat .env.local | xargs) && PYTHONPATH=. alembic revision --autogenerate -m "Add users and shapes"
	echo See Makefile for command

.PHONY: db-upgrade
db-upgrade:  ## Upgrade database schema with alembic
	export $$(cat .env.local | xargs) && PYTHONPATH=. alembic upgrade head

.PHONY: pg
pg: ## Connect to running local postgres database
	$$(PSQL) -p5432 "geox"
