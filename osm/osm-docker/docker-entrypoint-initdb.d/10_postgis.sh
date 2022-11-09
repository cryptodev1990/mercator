#!/bin/bash
# Copied from https://github.com/postgis/docker-postgis/blob/34f8447587f9985eb7bc48ffaae90118b81075f6/14-3.3/initdb-postgis.sh

set -e

# Perform all actions as $POSTGRES_USER
export PGUSER="$POSTGRES_USER"

# Create the 'template_postgis' template db
"${psql[@]}" <<- 'EOSQL'
CREATE DATABASE template_postgis IS_TEMPLATE true;
EOSQL

# Load PostGIS into both template_database and $POSTGRES_DB
for DB in template_postgis "$POSTGRES_DB"; do
	echo "Loading PostGIS extensions into $DB"
	"${psql[@]}" --dbname="$DB" <<-'EOSQL'
		CREATE EXTENSION IF NOT EXISTS postgis;
		-- comment out unneded extensions
		-- CREATE EXTENSION IF NOT EXISTS postgis_topology;
		-- Reconnect to update pg_setting.resetval
		-- See https://github.com/postgis/docker-postgis/issues/288
		\c
		-- CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
		-- CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;
EOSQL
done
