# Load OSM

Create a Docker container that loads a subset of OpenStreetMap data into PostGIS using [osm2pgsql](https://osm2pgsql.org/).

Build and start the container in the backgroud

```shell
docker compose up --build -d
```

The first time the container is started it will load data into the database which will take minutes.

To see the logs:

```
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
