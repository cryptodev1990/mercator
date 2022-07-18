#! /usr/bin/env sh
# Copied from https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/tests-start.sh
set -e

python -m app.tests_pre_start
alembic upgrade head
bash ./bin/test.sh "$@"
