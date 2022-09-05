# GEOX-UPLOADER

API to handle converting arbitrary geo formats to GeoJSON.
The API is performant, secure, stateless, and idempotent, for a wide range
of geoshapes, most importantly zipped shapefiles, XLS, and CSVs.

## TODO

- [ ] Sniff geometry column from a CSV, parquet, and convert the other columns to properties
- [ ] Reproject non-WGS84 / SRID 4326 into that projection
- [ ] Error on invalid geometries

## Limitations

- File size is capped at 20 MB for now.

## Example

`yarn run dev`

then separately

`curl -X POST http://localhost:8080/upload -F 'data=@/Users/andrewduberstein/Downloads/tl_2021_01015_roads.zip'`

or some other zipped shape file.

## Goals

- Converts zipped shapefiles, KML, XLS, and CSV into GeoJSON
- Converts WKT/WKB columns into valid GeoJSON geometries
- Reprojects non-WGS84 into that projection
- Errors on invalid geometries and notifies the user

## Development

`docker build -t geox-uploader . && docker run -p 8080:8080 geox-uploader`
