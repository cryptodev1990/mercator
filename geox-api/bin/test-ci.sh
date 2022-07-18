#! /usr/bin/env sh

# Exit in case of error
set -e

docker-compose -f docker-compose.yml -f docker-compose.ci.yml build
docker-compose -f docker-compose.yml -f docker-compose.ci.yml down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker-compose -f docker-compose.yml -f docker-compose.ci.yml up -d
docker-compose -f docker-compose.yml -f docker-compose.ci.yml exec -T app bash /webapp/tests-start.sh "$@"
docker-compose -f docker-compose.yml -f docker-compose.ci.yml down -v --remove-orphans
