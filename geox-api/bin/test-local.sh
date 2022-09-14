#!/usr/bin/env bash
# Run a tests locally.
# This uses a docker container for postgis that it creates
DOCKER_CONTAINER_NAME=geox-api-local-test

# Run and start docker container
export POSTGRES_USER=postgres
export POSTGRES_SERVER=localhost
export POSTGRES_DB=geox_test
export POSTGRES_PASSWORD=admin
export POSTGRES_PORT=5433
export POSTGRES_CONNECTION=postgresql+psycopg2://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_SERVER:$POSTGRES_PORT/$POSTGRES_DB

# quit container - remove container
# https://stackoverflow.com/a/38576401/227406
if [ ! "$(docker ps -q -f name=$DOCKER_CONTAINER_NAME)" ]; then
    if [ "$(docker ps -aq -f status=exited -f name=$DOCKER_CONTAINER_NAME)" ]; then
        # cleanup
        docker rm $DOCKER_CONTAINER_NAME
    fi
    # run your container
    docker run --name $DOCKER_CONTAINER_NAME -p "$POSTGRES_PORT:5432" \
        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        -e POSTGRES_USER=$POSTGRES_USER \
        -e POSTGRES_DB=$POSTGRES_DB \
        -d postgis/postgis
fi

# wait 10
ENV_FILE=.env.local ./tests-start.sh "$@"

docker stop $DOCKER_CONTAINER_NAME
docker container rm $DOCKER_CONTAINER_NAME
