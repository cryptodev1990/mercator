# OSM Search API

## Setup OSM PostGIS Database

The following commands should set up an OSM database that will work with the API.
It is not formalized into a script because it is not worth handling errors yet.

**Host postgres:**

This assumes that PostgreSQL and PostGIS are installed and running on the host.

```shell
curl -O osm.pbf https://download.geofabrik.de/north-america/us/california/norcal-latest.osm.pbf
just db-local osm osm.pbf
```

You will need to install [just](https://github.com/casey/just) to use the `just` command.

**Docker:**

```shell
cd osm-docker
curl -O osm.pbf https://download.geofabrik.de/north-america/us/california/norcal-latest.osm.pbf
docker compose up -d
```

With the default settings, that database runs as: `postgres@localhost:5238/postgres`.

## Configuration

See `.env.template` for examples of the environment variables.

See `app.core.config.Settings` for the env variables used to configure the app.

- all env variables are prefixed by `APP_`
- env variables are case-insensitive


## Run

Install poetry: https://python-poetry.org/docs/

Install dependencies:

```shell
poetry install
```

If there is a failure on linux due to a keyring issue, run the following command:
```
export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring
```

Start the app:

```shell
just run
```

See the API docs in dev: https://localhost:8080/docs.
