# Makefile to build and run Mercator GeoX app
#
# This is a self-documenting makefile. See
# Self documenting makefile https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

SHELL := bash
.DEFAULT_GOAL := help

PSQL_BIN ?= psql
RSCRIPT ?= RScript

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

.PHONY: dev-install
dev-install:  ## Install dependencies for local development
	./bin/install-dependencies-local.sh

.PHONY: dev
dev:  ## Run app locally
	export $$(cat .env.local | xargs) && overmind start

.PHONY: lint
lint: ## Lint the project
	# Lint the project
	black . --exclude py-geolift --exclude env

.PHONY: deploy
deploy: ## Deploy the project to flyctl
	test `command -v flyctl` || (echo "\033[31m Please install flyctl from fly.io" && exit -1);
	flyctl deploy

.PHONY: test
test: ## Run tests
	pytest -x -vvv .

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
	$(PSQL) -p5432 "geox"
