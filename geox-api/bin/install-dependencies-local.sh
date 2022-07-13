#!/bin/bash
# Install prerequisites for local development
# Exit on error
set -e

# Install Postgres
brew install postgresql
# Create geox database
createdb geox || true

# Install python dependencies
source env/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
deactivate

if ! command -v overmind &> /dev/null
then
    brew install overmind
else
    echo "overmind already installed"
fi
