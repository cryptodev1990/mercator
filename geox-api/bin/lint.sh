#!/usr/bin/env bash
# Lints all files in the project
set -x
# do not set -e because we want to run all the commands

# Lint python files
_lint_python() {
    mypy ./app
    black ./app --check
    isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --check-only

}

# Lint shell scripts (*.sh)
_lint_shell() {
    shellcheck -e SC1090 -S warning -- *.sh bin/*.sh
}

# Lint yaml with https://github.com/adrienverge/yamllint
_lint_yaml() {
    yamllint ./*.yml
}

# TODO: could customize which are run
_lint_python
_lint_shell
_lint_yaml
