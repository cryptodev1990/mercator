#!/bin/sh
wget https://download.geofabrik.de/north-america/us-west-latest.osm.pbf
java -Ddw.server.application_connectors[0].bind_host=0.0.0.0 -Ddw.server.application_connectors[0].port=8080 -Ddw.graphhopper.datareader.file=us-west-latest.osm.pbf -jar *.jar server config.yml
