#!/usr/bin/env sh
#
# Run an arbitrary command with env variables defined in a file
# Use environment variable ENV_FILE to set the environment
#
# Examples:
#
# run-with-env env
# ENV_FILE=.env.docker run-with-env env
export ENV_FILE=${ENV_FILE:-.env}
if [ ! -f "$ENV_FILE" ]; then
    export $(grep -v '^#' $ENV_FILE | xargs)
fi
exec "$@"
