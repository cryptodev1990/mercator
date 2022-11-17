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

MODULE_NAME=${MODULE_NAME:-app.main}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

APP_HOST=${APPHOST:-0.0.0.0}
APP_PORT=${APP_PORT:-8080}
APP_LOG_LEVEL=${APP_LOG_LEVEL:-info}

exec uvicorn --reload --host "$APP_HOST" --port "$APP_PORT" --log-level "$APP_LOG_LEVEL" "$APP_MODULE"
