-- Performance-focused change that skips compression for geoms
ALTER TABLE osm ALTER COLUMN geom SET STORAGE EXTERNAL;

UPDATE osm SET geom = ST_SetSRID(geom, 4326);
