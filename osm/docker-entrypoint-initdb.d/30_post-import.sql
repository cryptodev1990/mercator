-- Create indexes on tables
CREATE INDEX ON lines USING GIN (to_tsvector('english', tags));
CREATE INDEX ON polygons USING GIN (to_tsvector('english', tags));
CREATE INDEX ON boundaries USING GIN (to_tsvector('english', tags));
CREATE INDEX ON routes USING GIN (to_tsvector('english', tags));
-- Add full-text columns to tables
ALTER TABLE points
ADD COLUMN fts tsvector GENERATED ALWAYS AS (TO_TSVECTOR('english', tags)) STORED;
CREATE INDEX ON points USING GIN (fts);
ALTER TABLE boundaries
ADD COLUMN fts tsvector GENERATED ALWAYS AS (TO_TSVECTOR('english', tags)) STORED;
CREATE INDEX ON boundaries USING GIN (fts);