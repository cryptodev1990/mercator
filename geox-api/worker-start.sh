#! /usr/bin/env bash
# Start celery workers
set -e
python -m app.celeryworker_pre_start
celery --app app.worker worker --loglevel=${APP_LOG_LEVEL:-info}
