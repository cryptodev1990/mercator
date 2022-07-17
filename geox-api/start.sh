#! /usr/bin/env sh
# Start the unicorn process to run the app
# - MODULE_NAME: default app.main
# - VARIABLE_NAME: default app
# - APP_MODULE: $MODULE_NAME:$VARIABLE_NAME
# - APP_PORT: default 8080
# - APP_HOST: default localhost
# - APP_LOG_LEVEL: default info
# - PRE_START_PATH: path to a pre-start script
set -e
set -x

# Copied from https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/d4014223e3d367c9fdf5a9cdd634280e06a84a97/docker-images/start-reload.sh

# TODO: added this to avoid ModuleNotFoundError: No module named 'app'
# this is probably indicative of some other problems in specifications
MODULE_NAME=${MODULE_NAME:-app.main}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

APP_HOST=${APPHOST:-0.0.0.0}
APP_PORT=${APP_PORT:-8080}
APP_LOG_LEVEL=${APP_LOG_LEVEL:-info}

__prestart_app() {
    # Put all pre-start logic in a function - easier to comment out or make conditional if needed
    # Let the DB start
    python -m app.backend_pre_start

    # Run migrations
    alembic upgrade head

    # Create initial data in DB
    python -m app.initial_data
}

__prestart_app

# Start Uvicorn with live reload if run as dev
if [ "$APP_ENV" = "dev" ]; then
    RELOAD="--reload"
else
    RELOAD=""
fi;
exec uvicorn $RELOAD --host "$APP_HOST" --port "$APP_PORT" --log-level "$APP_LOG_LEVEL" "$APP_MODULE"
