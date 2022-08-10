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
    brew install rust openssl@1.1
    python3 -m venv env
    source env/bin/activate
    # Update pip and install wheel before isntalling anything else
    pip install --update wheel pip
    env LDFLAGS="-L$(brew --prefix openssl@1.1)/lib" CFLAGS="-I$(brew --prefix openssl@1.1)/include" pip install -r requirements.txt
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
