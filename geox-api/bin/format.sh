#!/bin/bash
# Format python files
set -e
echo "Running black"
black .
echo "Running isort"
isort --quiet .
