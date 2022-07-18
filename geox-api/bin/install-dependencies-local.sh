#!/bin/bash
# Install prerequisites for local development
# Exit on error
set -e

_install_db() {
    # Install Postgres
    echo "installing postgres"
    brew install -q postgresql postgis

    # Create geox database
    echo "Creating geox db/"
    createdb geox &>/dev/null || true
}

# Install python dependencies
_setup_python() {
    echo "Creating Python virtual environment at ./env"
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    deactivate
}

_install_overmind() {
    echo "Installing overmind"
    brew install -q overmind
}

_copy_template() {
    if [ ! -f ".env.local" ]; then
        echo "Copying .env.template to .env.local. Remember to fill it in!"
        cp .env.template .env.local
    else
        echo "Found existing .env.local."
    fi
}

brew update
_install_db
_setup_python
_install_overmind
_copy_template
