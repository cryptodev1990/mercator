#!/usr/bin/env bash
# Run a tests locally.

# # Run and start docker container
POSTGRES_USER=$(whoami)
export POSTGRES_USER
export POSTGRES_SERVER=localhost
export POSTGRES_DB=geox_test
export POSTGRES_PASSWORD=
export POSTGRES_PORT=5432
export POSTGRES_CONNECTION=

# Need to flush redis cache - TODO: how to only flush relevant redis keys if redis could be used by multiple apps
redis-cli flushdb
# TODO: do this better. Drop and recreate database for safety, but that is slow and not necessarily
dropdb $POSTGRES_DB
createdb $POSTGRES_DB

# wait 10
ENV_FILE=.env.local ./tests-start.sh "$@"
