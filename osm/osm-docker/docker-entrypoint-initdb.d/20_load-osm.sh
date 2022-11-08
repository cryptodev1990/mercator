#!/bin/bash
set -x
osm2pgsql -d postgres -U $POSTGRES_USER -O flex -S /data/custom.lua ${OSM2PGSQL_EXTRA_ARGS} /data/osm.pbf
