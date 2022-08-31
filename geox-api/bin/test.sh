#! /usr/bin/env sh

# Exit in case of error
set -e

pytest --cov=app --cov-report=term-missing "${@}"
