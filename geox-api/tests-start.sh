#! /usr/bin/env sh
# Copied from https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/tests-start.sh
set -e

# TODO: added this to avoid ModuleNotFoundError: No module named 'app'
# this is probably indicative of some other problems in specifications
export PYTHONPATH=.

python -m app.tests_pre_start
bash ./bin/test.sh "$@"
