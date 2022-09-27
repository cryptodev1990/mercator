#!/usr/bin/env bash
# Lints all files in the project
# do not set -e because we want to run all the commands

function check_status {
    "$@"
    local status=$?
    if (( status != 0 )); then
        echo "error with $1" >&2
    fi
    return $status
}

# Lint python files
function _mypy() {
    echo "Running mypy"
    mypy .
}

# Lint shell scripts (*.sh)
function _shellcheck() {
    echo "Running shellcheck"
    shellcheck -e SC1090 -S warning -- *.sh bin/*.sh
}

# Lint yaml with https://github.com/adrienverge/yamllint
function _yamllint() {
    echo "Running yamllint"
    # Relaxed is less strict about some things
    # See https://yamllint.readthedocs.io/en/stable/configuration.html#default-configuration
    yamllint -c yamllint.yml ./*.yml
}

# TODO: could customize which are run

cmds="_mypy _shellcheck _yamllint"
num_failures=0
for cmd in $cmds;
do
    check_status $cmd
    # increment if failed
    let num_failures+=$?
done
# Exit code is the number of failed tests
exit $num_failures
