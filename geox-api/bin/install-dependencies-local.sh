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
    python3 -m venv env
    source env/bin/activate
    # Update pip and install wheel before installing anything else
    pip install --upgrade wheel pip

    if [[ `uname` = "Darwin" ]]; then
        env LDFLAGS="-L$(brew --prefix openssl@1.1)/lib" CFLAGS="-I$(brew --prefix openssl@1.1)/include" pip install -r requirements.txt
    else
        pip install -r requirements.txt
    fi

    pip install -r requirements-dev.txt
    deactivate
}

_install_overmind() {
    if ! which overmind > /dev/null; then
        if [[ `uname` = "Darwin" ]]; then
            echo "Installing overmind"
            brew install -q overmind
        else
            echo "Install overmind before proceeding"
            exit 1
        fi
    fi
}

_install_just() {
    if ! which just > /dev/null; then
        if [[ `uname` = "Darwin" ]]; then
            echo "Installing just"
            brew install -q rust just
        else
            echo "Instll just before proceeding: https://github.com/casey/just"
            exit 1
        fi
    fi
}

_install_redis() {
    if ! which redis-cli > /dev/null; then
        if [[ `uname` = "Darwin" ]]; then
            echo "Installing redis"
            brew install -q redis
        else
            echo "Install redis before continuing"
            exit 1
        fi
    fi
}

_install_playright() {
    playwright install
}

if [[ `uname` = "Darwin" ]]; then
    brew upgrade && brew update

    if ! which brew > /dev/null; then
        echo "Install brew before continuing"
        exit
    fi
fi

_check_postgres
_install_just
_install_redis
_install_overmind
_setup_python
_install_playright
