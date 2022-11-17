FROM postgres:14-bullseye
ARG osm2pgsql_input_data=osm.pbf
ARG osm2pgsql_style=style.lua

# Upgrade using backports to get osm2pgsql 1.7+
RUN echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list

# Postgis copied from https://github.com/postgis/docker-postgis/blob/34f8447587f9985eb7bc48ffaae90118b81075f6/14-3.3/Dockerfile
ENV POSTGIS_MAJOR 3
ENV POSTGIS_VERSION 3.3.1+dfsg-1.pgdg110+1

RUN apt-get update \
      && apt-cache showpkg postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR \
      && apt-get install -y --no-install-recommends \
           # ca-certificates: for accessing remote raster files;
           #   fix: https://github.com/postgis/docker-postgis/issues/307
           ca-certificates \
           \
           postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR=$POSTGIS_VERSION \
           postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR-scripts \
      && rm -rf /var/lib/apt/lists/*

COPY ./docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/

RUN apt-get update \
    && apt-get -t bullseye-backports -y install osm2pgsql \
    && rm -rf /var/lib/apt/lists/*

# Set default config
# COPY osm-postgresql.conf /etc/postgresql/postgresql.conf

WORKDIR /data

COPY ${osm2pgsql_input_data} ${osm2pgsql_style} /data/
