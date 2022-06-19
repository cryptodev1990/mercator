.PHONY: test

setup:
	# Set up for local development
	python3 -m venv env; \
	pip install -r requirements.txt; \
	pip install -r requirements-dev.txt; \
	test `command -v docker` || (echo "\033[31m Please install docker" && exit -1); \
	test `command -v flyctl` || (echo "\033[31m Please install flyctl from fly.io" && exit -1);
run:
	# Run the production container
	docker run -p 8080:8080 geox-web:latest
build:
	# Build the production container
	DOCKER_BUILDKIT=0 docker build . -t geox-web:latest
lint:
	# Lint the project
	black .
deploy:
	# Deploy the project
	flyctl deploy
test:
	pytest -x -vvv .
