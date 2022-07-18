#!/usr/bin/env bash
# Lints all files in the project
set -x

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

# TODO: could customize which are run
_lint_python
_lint_shell