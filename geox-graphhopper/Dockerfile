FROM israelhikingmap/graphhopper
RUN apt-get update && apt-get install wget
RUN wget https://download.geofabrik.de/north-america/us/california-latest.osm.pbf
EXPOSE 8080
# RUN /graphhopper/graphhopper.sh --url california-latest.osm.pbf --host 0.0.0.0 --port 8080
RUN /bin/bash
