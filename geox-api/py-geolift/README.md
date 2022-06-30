# PyGeoLift

A python wrapper for the [GeoLift](https://github.com/facebookincubator/GeoLift) R package.

## Prerequisites

Install the latest version of R (`R>=4.2.1`) from [CRAN](https://cloud.r-project.org/) or brew (`brew install r-base`)

In the terminal run the following script to install the R package [GeoLift](https://github.com/facebookincubator/GeoLift) and dependencies.

```shell
Rscript dependencies.R
```

Python dependencies and virtual environments are managed by [Poetry](https://python-poetry.org/).

Install and setup poetry using these [instructions](https://python-poetry.org/docs/#installation).

Run the following to install python dependencies for development.

```shell
poetry install
```

## Running

To use the virtual environment with the python dependencies, run the following.

```shell
poetry shell
```

From there you can launch Jupyter from the command line or use other python packages.

In [VSCode select the virtual environment](https://code.visualstudio.com/docs/python/environments#_select-and-activate-an-environment) that is listed when you run `poetry env list`.

## Common Problems

If `rpy2` cannot find the R installation, ask for help.
