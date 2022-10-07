#!/bin/bash
# Install prerequisites for local development
# Exit on error
set -e

_check_postgres() {
    if ! which psql > /dev/null
    then
        echo "Install PostgreSQL 14 before proceeding!" 1>&2
        exit 1
    else
        echo "Postgres installed"
    fi;
}

# Install python dependencies
_setup_python() {
    echo "Creating Python virtual environment at ./env"
    brew install rust openssl@1.1
    python3 -m venv env
    source env/bin/activate
    # Update pip and install wheel before isntalling anything else
    pip install --upgrade wheel pip
    env LDFLAGS="-L$(brew --prefix openssl@1.1)/lib" CFLAGS="-I$(brew --prefix openssl@1.1)/include" pip install -r requirements.txt
    pip install -r requirements-dev.txt
    deactivate
}

_install_overmind() {
    if ! which overmind > /dev/null; then
        echo "Installing overmind"
        brew install -q overmind
    fi
}

_install_just() {
    if ! which just > /dev/null; then
        echo "Installing just"
        brew install -q rust just
    fi
}

_install_redis() {
    if ! which redis-cli > /dev/null; then
        echo "Installing redis"
        brew install -q redis
    fi
}

brew upgrade && brew update
_check_postgres
_install_redis
_install_overmind
_install_just
_setup_python
