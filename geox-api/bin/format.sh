#!/bin/bash
# Format python files
black .
isort --quiet .
