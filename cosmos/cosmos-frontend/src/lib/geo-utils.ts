import { bbox } from "@turf/turf";
import { FeatureCollection } from "src/store/search-api";

export function bboxToZoom({
  latMin,
  latMax,
  lngMin,
  lngMax,
}: {
  latMin: number;
  latMax: number;
  lngMin: number;
  lngMax: number;
}): number {
  let zoomLevel;
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

function featureCollectionToBounds(fc: FeatureCollection) {
  // loop through all features and get bounds
  if (!fc?.features?.length) throw new Error("No features found");
  const bounds = fc.features.reduce(
    (acc, feature) => {
      const featureBounds = bbox(feature);
      if (featureBounds[0] < acc[0]) acc[0] = featureBounds[0];
      if (featureBounds[1] < acc[1]) acc[1] = featureBounds[1];
      if (featureBounds[2] > acc[2]) acc[2] = featureBounds[2];
      if (featureBounds[3] > acc[3]) acc[3] = featureBounds[3];
      return acc;
    },
    [Infinity, Infinity, -Infinity, -Infinity]
  );
  return {
    latMin: +bounds[1],
    latMax: +bounds[3],
    lngMin: +bounds[0],
    lngMax: +bounds[2],
  };
}

export const snapToBounds = (fc: FeatureCollection) => {
  // get bounding box of all shapes
  if (!fc?.features?.length) throw new Error("No features found");
  const { latMin, latMax, lngMin, lngMax } = featureCollectionToBounds(fc);
  console.log("bounds", { latMin, latMax, lngMin, lngMax });
  const centroid = [(lngMin + lngMax) / 2, (latMin + latMax) / 2];
  const zoom = bboxToZoom({ latMin, latMax, lngMin, lngMax });
  console.log("zoom", zoom);

  if (!zoom) return;
  if (!Number.isFinite(centroid[0]) || !Number.isFinite(centroid[1])) return;

  return {
    latitude: centroid[1],
    longitude: centroid[0],
    zoom,
  };
};

const utils = {
  snapToBounds,
};

export default utils;
