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

Settings for `.env`:

```shell
ENV=DEV
DB__DATABASE=
DB__USER=
DB__PASSWORD=
DB__PORT=
DB__HOST=
```

See `app.core.config.Settings` for the env variables used to configure the app.

## Run

Install poetry: https://python-poetry.org/docs/

Install dependencies:

```shell
poetry install
```

Start the app:

```shell
just run
```

See the API docs in dev: https://localhost:8080/docs.
