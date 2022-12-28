-- Create indexes
CREATE INDEX ON osm (id);
CREATE INDEX ON osm (osm_type);
CREATE INDEX ON osm (osm_id);

-- GIN will index operations on the tags column: ?, ?|, ?&, @>, @@, @?
CREATE INDEX ON osm USING GIN (tags);

ALTER TABLE osm ADD COLUMN fts tsvector GENERATED ALWAYS AS (to_tsvector('english', tags )) STORED;
CREATE INDEX ON osm USING GIN (fts);

-- index geometry types
ALTER TABLE osm ADD COLUMN geometry_type TEXT GENERATED ALWAYS AS (GeometryType(geom)) STORED;
CREATE INDEX ON osm (geometry_type);

-- Need GIN for ?, ?|, ?&, @>, @@, @? ops
CREATE INDEX on osm USING GIN (tags);
-- CREATE INDEX on osm USING GIST (tags);
