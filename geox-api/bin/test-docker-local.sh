#! /usr/bin/env bash
# copied from https://raw.githubusercontent.com/tiangolo/full-stack-fastapi-postgresql/master/%7B%7Bcookiecutter.project_slug%7D%7D/scripts/test-local.sh

# Exit in case of error
set -e

docker-compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error

if [ "$(uname -s)" = "Linux" ]; then
    echo "Remove __pycache__ files"
    sudo find . -type d -name __pycache__ -exec rm -r {} \+
fi

docker-compose build
docker-compose up -d
docker-compose exec -T app bash /webapp/tests-start.sh "$@"
