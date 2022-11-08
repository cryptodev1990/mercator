# Load OSM

## Local

The following commands should set up an OSM database that will work with the API.
It is not formalized into a script because it is not worth handling errors yet.

Assumes that postgres + postgis is running locally.

```shell
createdb osm
psql osm -c "CREATE EXTENSION postgis"
# whatever pbf file you want
curl -O osm.pdf https://download.geofabrik.de/north-america/us/california/norcal-latest.osm.pbf
osm2pgsql -d osm -O flex -S osm-docker/style.lua default.style osm.pbf
psql osm -f osm-docker/docker-entrypoint-initdb.d/30_post-import.sql
```

## Docker

Create a Docker container that loads a subset of OpenStreetMap data into PostGIS using [osm2pgsql](https://osm2pgsql.org/).

Build and start the container in the backgroud

```shell
docker compose up --build -d
```

The first time the container is started it will load data into the database which will take minutes.

To see the logs:

```shell
docker compose logs osm
```

To connect to the container from the host:

```shell
psql -U postgres -P 2538 osm
```

To connect to the container directly:

```shell
docker compose up osm -it bash
```

or

```shell
docker compose up osm -it psql -U postgres
```

The database data is stored in a persistant docker container listed in `docker-compose.yml`.

Notes:

- the downloaded data file is hardcoded right now. When it is time to generalize this, make it an env variable.
