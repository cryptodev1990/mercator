import { GeoShape } from "../../client";

export function geoShapesToFeatureCollection(shapes: GeoShape[] | undefined) {
  if (!shapes) {
    return [];
  }
  return {
    type: "FeatureCollection",
    features: !shapes
      ? []
      : shapes.map(({ name, geojson }: GeoShape) => {
          return {
            type: "Feature",
            geometry: geojson.geometry,
            properties: {
              name,
            },
          };
        }),
  };
}
