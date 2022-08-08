# GeoX API


The justfile is the documentation for tasks for now. [Just](https://github.com/casey/just) is a command line runner similar to make.

To see the commands, run (after installing `just`):

```shell
just
```

Other important information:

- Deploys are on fly.io.
- Frontend is in a sibling directory to this one.
- ``app`` is the FastAPI web app.

## Build and Insall Cases

1. Build and deploy to fly.io with Docker
2. Develop locally on MacOS
3. Develop locally with Docker
4. Test on GitHub

The file `.env.template` shows the env variables needed for this.

To support the various use cases here, it is a good idea **NOT TO USE** a an `.env` file because various tools in the app apply a strong precedence to `.env` files making it difficult to override those environment variables later.

### MacOS

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

## Docker (self-contained build)

This builds an image of the app, including the files needed into the image (as in deployment), and uses Docker images of redis and postgres.
The postgres database is stored in a Docker volume to persist it.
The relevant files are:

- `docker-compose.yml`
- `Dockerfile`

The environment variables are read from the file `.env.docker`.

Define the relevant ENV variables in `.env.docker`.

To build the image (`docker-compose build`)

```shell
just docker-build
```

To start all the services (`docker-compose up`):

```shell
just docker-up
```

To shell into the app's running container:

```shell
just docker-exec
```

To shell into a different service's container:

```shell
just docker-exec db bash
```

The app's database data is persisted in a Docker volume, `geox-app-db-data`.
To delete the data in the database, run:

```shell
just docker-delete-db
```

## Docker Development Build

The docker dev recipes will build an image of the app with the necessary Python dependencies, and use docker containers for redis and postgres.
Unlike, the self-contained build, the dev build uses the local app files and restarts the server when any app files are changed.

The relevant files are:

- `docker-compose.override.yml` - overrides settings in `docker-compose.yml`
- `Dockerfile.dev`

## Scripts

### start.sh

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

## References

- <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker>
- <https://github.com/tiangolo/uvicorn-gunicorn-docker>
