#!/bin/bash
# Install prerequisites for local development
# Exit on error
set -e

# Install pygeolift dependencies
if ! command -v Rscript &> /dev/null
then
    echo "R is not installed!"
    exit1
fi
Rscript --verbose py-geolift/dependencies.R

# Build the pygeolift package
make -C py-geolift build


# Install redis
if ! command -v redis &> /dev/null
then
    brew install redis
fi

# Install Postgres
brew install postgresql
# Create geox database
createdb geox || true

# Install python dependencies
source env/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install ./py-geolift/dist/pygeolift-*-py3-none-any.whl
deactivate

if ! command -v overmind &> /dev/null
then
    brew install overmind
else
    echo "overmind already installed"
fi
