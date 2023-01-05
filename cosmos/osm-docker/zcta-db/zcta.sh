#!/bin/bash
set -e

wget https://www2.census.gov/geo/tiger/TIGER2022/ZCTA520/tl_2022_us_zcta520.zip
tar -xvzf tl_2022_us_zcta520.zip
shp2pgsql -s 4326 \
  -I -D \
  tl_2022_us_zcta520.shp \
  zcta_polys \
  | psql --user osmuser -d osm
rm -f tl_2022_us_zcta520.*

psql --user osmuser -d osm -c "ALTER TABLE 
