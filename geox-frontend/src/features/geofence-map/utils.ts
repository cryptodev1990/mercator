import { GeoShapeCreate, GeoShape } from "../../client";

export function geoShapesToFeatureCollection(
  shapes: GeoShape[] | GeoShapeCreate[]
) {
  /**
   * Converts GeoShapes to GeoJSON FeatureCollection
   */
  const isNullOrUndefined = typeof shapes === "undefined" || !shapes;
  return {
    type: "FeatureCollection",
    features: isNullOrUndefined
      ? []
      : shapes.map(({ geojson }: GeoShape | GeoShapeCreate) => {
          return {
            type: "Feature",
            geometry: geojson!.geometry,
            properties: {
              ...geojson!.properties,
            },
          };
        }),
  };
}

export function featureToFeatureCollection(features: any[] | null | undefined) {
  /**
   * Converts GeoShapes to GeoJSON FeatureCollection
   */
  if (!features) {
    return { type: "FeatureCollection", features: [] };
  }
  return {
    type: "FeatureCollection",
    features,
  };
}

export function bboxToZoom(bbox: any): Number {
  let zoomLevel;
  const [latMin, latMax, lngMin, lngMax] = bbox;
  const latDiff = +latMax - +latMin;
  const lngDiff = +lngMax - +lngMin;
  const maxDiff = lngDiff > latDiff ? lngDiff : latDiff;
  if (maxDiff < 360 / Math.pow(2, 20)) {
    zoomLevel = 21;
  } else {
    zoomLevel =
      -1 * (Math.log(maxDiff) / Math.log(2) - Math.log(360) / Math.log(2));
    if (zoomLevel < 1) {
      zoomLevel = 1;
    }
  }
  return zoomLevel;
}
