#!/usr/bin/env bash
set -x

mypy ./app
black ./app --check
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --check-only
