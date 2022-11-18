-- CREATE TYPE ST_Direction4 AS ENUM ('north', 'south', 'east', 'west');

CREATE OR REPLACE FUNCTION ST_GetDirection(azimuth DOUBLE PRECISION)
RETURNS TEXT
LANGUAGE sql
IMMUTABLE
AS
$$
SELECT CASE
WHEN azimuth <= 45 THEN 'north'
WHEN azimuth <  135 THEN 'east'
WHEN azimuth <= 225 THEN 'south'
WHEN azimuth < 315 THEN 'west'
ELSE 'north'
END;
$$;

CREATE OR REPLACE FUNCTION ST_GetDirection(a GEOMETRY, b GEOMETRY)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS
$$
SELECT ST_GetDirection(ST_Azimuth(ST_Centroid(a), ST_Centroid(b)));
$$;
