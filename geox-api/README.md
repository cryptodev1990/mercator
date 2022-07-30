GeoX API
=========

The Makefile is the documentation for tasks for now. Check the Makefile by running

```shell
make
```

- Deploys are on fly.io.
- Frontend is in a sibling directory to this one.
- ``app`` is the FastAPI web app.

Build and Running Cases
-----------------------

1. Build and deploy to fly.io with Docker
2. Develop locally on MacOS
3. Develop locally with Docker
4. Test on GitHub

Local Install
-------------

Local install and development only supported for MacOS.

This assumes that you have [brew](https://brew.sh/) installed.

Install dependencies and setup environment by running this script in this directory.

```shell
make dev install
```

This will:

- Install dependencies (e.g. Postgres, Overmind)
- Create a Postgres database `geox`
- Create a Python environment at `./env` and install packages there
- Create the env file `.env.local`.

After this you will need to do the additional manual steps:

- Fill in all the environment variables in `./.env.local`
- Ensure the postgres server is running `brew services start postgres`

Check that you can connect to the `geox` database.

```shell
psql geox
```

Docker
--------------------

There are three Docker images defined in these Dockeriles:

- `Dockerfile`: Build app for deployment
- `Dockerfile.dev`: Develop app with Docker. This uses the local filesystem.
- `Dockerfile.ci`: Similar to `Dockerfile`, but the build includes files and dependencies used for development and testing.

Define the relevant ENV variables in `.env.docker`.

When developing with Docker, use this:

```shell
docker-compose build
docker-compose up -d
```

This workflow also containerized postgres database, but uses the app host files so that source changes made while the app is running will be used in the app.

These make targets can also be used to build, run, and connect to the app running in Docker containers.

```shell
make docker-build
make docker-run
make docker-connect
```

Build and containers similar to deployment. This uses a containerized postgres database, and includes app source code in the image.

```shell
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up -d
```


To run CI tests with docker,

```shell
./bin/test-ci.sh
```

Scripts
----------

`start.sh`
++++++++++

Script that starts the app. It starts and initializes the database before starting the app.

The script `start.sh` uses these environment variables to customize its behavior.

- `APP_RELOAD`: If set to "1" or "true", will run the app in reload mode. Default is not to reload the app.
- `APP_NO_ALEMBIC`: If set to "1" or "true", then **do not run alembic on startup. Default is to run `alembic upgrade` on start.
- `MODULE_NAME`: Name of the Python module where the FastAPI app is defined. Default is `app.main`.
- `VARIABLE_NAME`: Name of the variable in `MODULE_NAME` that defines the FastAPI app is defined. Default is `app`.
- `APP_HOST`. Host name to run the app on. Default is "0.0.0.0".
- `APP_PORT`. Port number to use for the app. Default is "8080".
- `APP_LOG_LEVEL`. Logging level to use with the
- `MODULE_NAME`. Name of the Python module where the FastAPI app is defined. Default is `app.main`.

References
----------

- <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker>
- <https://github.com/tiangolo/uvicorn-gunicorn-docker>
