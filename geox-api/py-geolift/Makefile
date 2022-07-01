# Makefile to build and run Mercator GeoX app
#
# This is a self-documenting makefile. See
# Self documenting makefile https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
SHELL := bash
RSCRIPT ?= RScript
.DEFAULT_GOAL := help

.PHONY: help
help:  ## Display available tasks
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build
build: ## Build Python package
	poetry build
