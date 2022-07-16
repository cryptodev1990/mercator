#! /usr/bin/env bash
# Copied from https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/tests-start.sh
set -e

PYTHONPATH=. python -m app.tests_pre_start

bash ./bin/test.sh "$@"
