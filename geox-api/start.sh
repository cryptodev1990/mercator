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
export PYTHONPATH=.

MODULE_NAME=${MODULE_NAME:-app.main}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

APP_HOST=${APPHOST:-localhost}
APP_PORT=${APP_PORT:-8080}
APP_LOG_LEVEL=${APP_LOG_LEVEL:-info}

# If there's a prestart.sh script in the /app directory or other path specified, run it before starting
PRE_START_PATH=${PRE_START_PATH:-./prestart.sh}
echo "Checking for script in $PRE_START_PATH"
if [ -f $PRE_START_PATH ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "There is no script $PRE_START_PATH"
fi

# Start Uvicorn with live reload
if [ "$APP_ENV" = "dev" ]; then
    RELOAD="--reload"
else
    RELOAD=""
fi;
exec uvicorn $RELOAD --host "$APP_HOST" --port "$APP_PORT" --log-level "$APP_LOG_LEVEL" "$APP_MODULE"
