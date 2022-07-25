#! /usr/bin/env bash
# Start celery workers
set -e

if [ "$(uname -s)" = "Darwin" ]; then
    brew services start redis 1>/dev/null
fi
python -m app.celeryworker_pre_start
celery --app app.worker worker --loglevel=info --queues main-queue
