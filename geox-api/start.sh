#! /usr/bin/env sh
set -e

# TODO: added this to avoid ModuleNotFoundError: No module named 'app'
# this is probably indicative of some other problems in specifications
export PYTHONPATH=.

PRE_START_PATH="./prestart.sh"
echo "Checking for script in $PRE_START_PATH"
if [ -f "$PRE_START_PATH" ] ; then
    echo "Running script $PRE_START_PATH"
    . "$PRE_START_PATH"
else
    echo "There is no script $PRE_START_PATH"
fi

# Start uvicorn

exec uvicorn app.main:app "$@"
