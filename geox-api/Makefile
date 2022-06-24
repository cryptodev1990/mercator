.PHONY: test

setup:
	# Set up for local development
	python3 -m venv env; \
	pip install -r requirements.txt; \
	pip install -r requirements-dev.txt; \
	test `command -v docker` || (echo "\033[31m Please install docker" && exit -1); \
	test `command -v flyctl` || (echo "\033[31m Please install flyctl from fly.io" && exit -1);
docker-run:
	# Run the production container
	docker run -p 8080:8080 --env-file .env.docker geox-web:latest
docker-build:
	# Build the production container
	DOCKER_BUILDKIT=0 docker build . -t geox-web:latest
build:
	pip install -r requirements.txt; \
	pip install -r requirements-dev.txt; \
        cd py-geolift; \
	Rscript --verbose dependencies.R; \
	poetry config virtualenvs.create false; \
    	poetry build; \
    	pip install dist/pygeolift-*.tar.gz; \
	cd ..; \
	brew install overmind

dev:
	export $$(cat .env.local | xargs) && overmind start

lint:
	# Lint the project
	black .
deploy:
	# Deploy the project
	flyctl deploy
test:
	pytest -x -vvv .

docker-connect:
	docker run -it geox-web:latest bash

db-revision:
	# alembic revision -m "$(msg)"
	# TODO how should this actually be done?
	# export $(cat .env.local | xargs) && PYTHONPATH=. alembic revision --autogenerate -m "Add users and shapes"
	echo See Makefile for command

db-upgrade:
	export $$(cat .env.local | xargs) && PYTHONPATH=. alembic upgrade head


pg:
	/Applications/Postgres.app/Contents/Versions/14/bin/psql -p5432 "geox"
