import { GeoShape } from "../../client";

export function geoShapesToFeatureCollection(shapes: GeoShape[] | undefined) {
  /**
   * Converts GeoShapes to GeoJSON FeatureCollection
   */
  if (!shapes) {
    return [];
  }
  return {
    type: "FeatureCollection",
    features: !shapes
      ? []
      : shapes.map(({ name, geojson, created_at, uuid }: GeoShape) => {
          return {
            type: "Feature",
            geometry: geojson.geometry,
            properties: {
              name,
              created_at,
              uuid,
            },
          };
        }),
  };
}
