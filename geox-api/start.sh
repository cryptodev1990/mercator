#! /usr/bin/env bash
# Start the hypercorn/unicorn process to run the app
# - MODULE_NAME: default app.main
# - VARIABLE_NAME: default app
# - APP_MODULE: $MODULE_NAME:$VARIABLE_NAME
# - APP_PORT: default 8080
# - APP_HOST: default localhost
# - APP_LOG_LEVEL: default info
# - PRE_START_PATH: path to a pre-start script
set -e

# Derived from https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/d4014223e3d367c9fdf5a9cdd634280e06a84a97/docker-images/start-reload.sh

# TODO: added this to avoid ModuleNotFoundError: No module named 'app'
# this is probably indicative of some other problems in specifications
MODULE_NAME=${MODULE_NAME:-app.main}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

APP_HOST=${APPHOST:-0.0.0.0}
APP_PORT=${APP_PORT:-8080}
APP_LOG_LEVEL=${APP_LOG_LEVEL:-info}
export DD_TRACE_ENABLED=${DD_TRACE_ENABLED:-false}

APP_WORKERS=${APP_WORKERS:-8}

__prestart_app() {
    # Put all pre-start logic in a function - easier to comment out or make conditional if needed
    # Let the DB start
    echo $PYTHONPATH
    echo $PWD
    python -m app.backend_pre_start

    # Run migrations
    if [ ! "$APP_NO_ALEMBIC" = "1" ] || [ ! "$(echo \"$APP_NO_ALEMBIC\" | tr '[:upper:]' '[:lower:]')" = "true" ]
    then
        alembic upgrade head
    fi

    # Create initial data in DB
    python -m app.initial_data
}

__prestart_app

# Start Uvicorn with live reload if APP_RELOAD is 1 or true; otherwise false
RELOAD_OPT=
if [ "$APP_RELOAD" = "1" ] || [ "$(echo \"$APP_RELOAD\" | tr '[:upper:]' '[:lower:]')" = "true" ]
then
    RELOAD_OPT="--reload"
fi;

exec hypercorn $RELOAD_OPT "$APP_MODULE" --workers $APP_WORKERS --bind "$APP_HOST":"$APP_PORT" --config hypercorn.toml
