#!/bin/bash
set -x
osm2pgsql -d postgres -U $POSTGRES_USER -O flex -S /data/default.style ${OSM2PGSQL_EXTRA_ARGS} /data/osm.pbf
