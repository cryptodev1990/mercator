#! /usr/bin/env sh

# Exit in case of error
set -e

pytest -x -vvv "${@}"
