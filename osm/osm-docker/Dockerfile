FROM postgis/postgis:14-3.3

# Upgrade using backports to get osm2pgsql 1.7+
RUN echo 'deb http://deb.debian.org/debian bullseye-backports main' >> /etc/apt/sources.list

RUN apt-get update \
    && apt-get -t bullseye-backports -y install osm2pgsql \
    && rm -rf /var/lib/apt/lists/*

# need curl to download stuff
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

ENV PBF_DOWNLOAD_URL https://download.geofabrik.de/north-america/us/california/norcal-latest.osm.pbf

WORKDIR /data
RUN curl -s -o osm.pbf ${PBF_DOWNLOAD_URL}

COPY generic.lua default.style
COPY ./docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/

WORKDIR /
