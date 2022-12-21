
/*

If a geometry is a collection, then the intersection of all the geometries in the collection is returned.

*/
CREATE OR REPLACE FUNCTION ST_UnaryIntersection(geom GEOMETRY)
RETURNS GEOMETRY
IMMUTABLE STRICT
LANGUAGE plpgsql
AS
$$
DECLARE
    i INTEGER;
    g GEOMETRY;
    intersected GEOMETRY;
BEGIN
    i = 0;
    FOR g IN SELECT (ST_Dump(geom)).geom
    LOOP
        i := i + 1;
        IF i = 1 THEN
            intersected := ST_Union(g);
        ELSE
            intersected := ST_Intersection(intersected, ST_Union(g));
        END IF;
        -- Once we have an empty geometry, we can stop
        IF ST_IsEmpty(intersected) THEN
            RETURN intersected;
        END IF;
    END LOOP;
    RETURN intersected;
END;
$$;

/*
SELECT ST_AsEWKT(ST_UnaryIntersect(ST_Collect(geom)))
FROM (
SELECT ST_GeomFromEWKT('POLYGON((0 0,0 1,1 1,1 0,0 0))')
UNION ALL
SELECT ST_GeomFromEWKT('POLYGON((0.5 0,0.5 1,1.5 1,1.5 0,0.5 0))')
) a(geom);
*/


CREATE OR REPLACE FUNCTION _st_intersects_agg_sfunc(a GEOMETRY, b GEOMETRY)
RETURNS GEOMETRY
STRICT
IMMUTABLE
LANGUAGE sql
AS
$$
SELECT ST_Intersection(ST_Union(a), ST_Union(b))
$$;

/*

Aggregate function that returns the intersection of all geometries in a set.

*/

CREATE OR REPLACE AGGREGATE ST_IntersectionAgg(g GEOMETRY) (
    SFUNC = _st_intersects_agg_sfunc,
    STYPE = GEOMETRY,
    COMBINEFUNC = _st_intersects_agg_sfunc
);

-- SELECT ST_AsText(ST_IntersectionAgg(geom))
-- FROM (
-- SELECT ST_GeomFromEWKT('POLYGON((0 0,0 1,1 1,1 0,0 0))')
-- UNION ALL
-- SELECT ST_GeomFromEWKT('POLYGON((0.5 0,0.5 1,1.5 1,1.5 0,0.5 0))')
-- ) a(geom);

-- SELECT ST_AsText(ST_IntersectionAgg(geom))
-- FROM (
-- SELECT ST_GeomFromEWKT('POLYGON((0 0,0 1,1 1,1 0,0 0))')
-- UNION ALL
-- SELECT ST_GeomFromEWKT('POLYGON((2 0,3 1,3 1,3 0,2 0))')
-- ) a(geom);
