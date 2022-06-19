run:
	docker run -p 8080:8080 geox-web:latest
build:
	DOCKER_BUILDKIT=0 docker build . -t geox-web:latest
lint:
	black .
deploy:
	flyctl deploy
