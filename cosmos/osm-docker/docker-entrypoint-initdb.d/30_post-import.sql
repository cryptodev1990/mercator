-- Create indexes on tables
ALTER TABLE osm
ADD COLUMN fts tsvector GENERATED ALWAYS AS (TO_TSVECTOR('english', tags)) STORED;
CREATE INDEX ON osm USING GIN (fts);
CREATE INDEX ON osm (osm_type);
CREATE INDEX ON osm (category);