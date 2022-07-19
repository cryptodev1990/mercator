#!/bin/bash
# Format python files
black ./app ./alembic/env.py
isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive ./app ./alembic/env.py
