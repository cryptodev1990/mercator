# GeoX API


The justfile is the documentation for tasks for now. [Just](https://github.com/casey/just) is a command line runner similar to make.

To see the commands, run (after installing `just`):

```shell
just
```

Other important links and information:

- Deploys are on [fly.io](https://fly.io/dashboard/geox).
- Frontend is in a sibling directory to this one.
- ``app`` is the FastAPI web app.
- Auth0 handles our [dev](https://manage.auth0.com/dashboard/us/dev-w40e3mxg/) and [production](https://manage.auth0.com/dashboard/us/mercator-prod/) auth.
- Our [AWS portal](https://us-east-1.console.aws.amazon.com/iamv2/home#/home) has S3 buckets we use to transfer data and some IAM roles we've configured for 3rd party apps.
- Our [Snowflake instance](https://app.snowflake.com/us-west-2/xga41918/) is used to transfer data to customers.
- Our waitlist and some of our image hosting is on Supabase [here](https://app.supabase.com/project/xmwdyaolhaobykjycchu) and [here](https://app.supabase.com/project/nkkohsotcmbtyzqpxukw/storage/buckets/logo)

## Build and Install Cases

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

## Environment Variables and Settings

Environment variables and dotenv files are used for configuration.

### Advice

- Avoid directly using the file `.env` because Overmind reads it with a high precedence that is
  difficult to override.
- Use different dotenv files for local and docker development

  - `.env.local`
  - `.env.docker`

- Don't set environment variables in

### Applications

#### App

- Reads dotenv file specified by the `ENV_FILE` environment variable.
  Does not read a file otherwise.
- Any environment variables in the shell take precendence over the dotenv file
  so be careful.
- Uses Pydantic settings to manage configs from environment variables and a dotenv file.

  - See `app.core.config` for the settings object
  - See [Pydantic docs](https://pydantic-docs.helpmanual.io/usage/settings/), [FastAPI docs](https://fastapi.tiangolo.com/advanced/settings/),

#### Justfile

- The `dotenv-load` will load environment variables from a `.env` file. It cannot be customized
  to read from different files, and shell variables generally override `.env` files in child
  processes. **DO NOT USE**

#### Docker and Docker compose

See [Docs](https://docs.docker.com/compose/environment-variables/).

- Sources

  - Command line `--env-file` arguments, e.g. `docker compose --env-file .env.docker ...`
  - `env_file` key in docker compose file to read from a dotenv file
  - `environment` key in docker compose to specify env variables directly
  - `ENV` command in a Dockerfile
  - shell variables at build or runtime

- Order of precedence

  - Compose file
  - Shell environment variables
  - Environment file
  - Dockerfile
  - Variable is not defined

#### Overmind

[Docs](https://github.com/mercatorhq/mercator/runs/7730555711?check_suite_focus=true#step:4:10)

- Sources:

  - Reads `.env` file by default
  - Reads `.overmind.env` for additional env variables
  - Set the variable `OVERMIND_SKIP_ENV` to not read `.env` file. Overmind will still read `.overmind.env` files
  - The env variable `OVERMIND_ENV` is used to add additional dotenv files to read.

- Order of precedence

  - `~/.overmind.env`
  - `./.overmind.env`
  - `./.env`
  - `$OVERMIND_ENV`

#### Github Actions

Set environment variables directly in the yml file if not secret, or use [Github secrets](https://docs.github.com/en/rest/actions/secrets) for
sensitive information.

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
