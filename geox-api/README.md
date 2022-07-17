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

Docker Install (WIP)
--------------------

Define the relevant ENV variables in `.env.docker`.

For dev work, this will start the app running on `localhost:8080`.

```shell
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

To connect to app container

```shell
docker exec -ti geox-api-app-dev /bin/bash
```

To initialize the tables in the database

```shell
docker exec geox-api-app-dev /usr/bin/env PYTHONPATH=. ./prestart.sh
```

To connect to DB container:

```shell
docker exec geox-api-app-dev /bin/bash
```

To connect to the DB container within the database

```shell
docker exec geox-api-app-dev /bin/env psql -U postgres geox
```

Changes made to files in the directory will be reloaded.
However, if new python requirements are added, the image needs to be rebuilt.

For prod, this will start the app:

```shell
docker-compose -f docker-compose.yml up
```

Linting
-------

```
bin/lint-shell.sh
```

References
----------

- https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
- https://github.com/tiangolo/uvicorn-gunicorn-docker

Organization
------------

- `start.sh`: Starts the app
