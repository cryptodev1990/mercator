#!/bin/bash
osm2pgsql -d postgres -U $POSTGRES_USER -O flex -S /data/generic.lua /data/osm.pbf
