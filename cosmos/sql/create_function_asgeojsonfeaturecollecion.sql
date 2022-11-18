CREATE OR REPLACE FUNCTION AsGeoJSONFeatureCollection(features JSONB)
RETURNS JSONB
AS
$$
DECLARE
  min_x DOUBLE PRECISION;
  min_y DOUBLE PRECISION;
  max_x DOUBLE PRECISION;
  max_y DOUBLE PRECISION;
BEGIN
    if jsonb_typeof(features) = 'object' then
        return jsonb_build_object('type', 'FeatureCollection', 'features', jsonb_build_array(features))
    end if;
    if jsonb_typeof(features) != 'array' then
      return null;
    end if;
    for feat in (select jsonb_array_elements(features)) loop
      if feat->'bbox' is null then
        continue;
      end if;
      min_x = least(min_x, feat->'{bbox,0}');
      min_y = least(min_x, feat->'{bbox,1}');
      max_x = greatest(max_x, feat->'{bbox,2}');
      max_y = greatest(max_y, feat->'{bbox,3}');
    end loop;
    return jsonb_build_object('type', 'FeatureCollection', 'features', features, 'bbox', jsonb_build_array(min_x, min_y, max_x, max_y));
END;
$$