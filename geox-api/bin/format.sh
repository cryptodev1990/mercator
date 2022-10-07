#!/bin/bash
# Format python files
set -e
echo "Running isort"
isort --quiet .
echo "Running black"
black .

# DEBUG: Mark as changed