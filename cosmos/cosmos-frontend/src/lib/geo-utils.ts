import { FeatureCollection, SearchResponse } from "../search/api";
import { bbox } from "@turf/turf";

export function bboxToZoom(bbox: number[]): number {
  let zoomLevel;
  const [lngMin, latMin, lngMax, latMax] = bbox;
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

export const snapToBounds = (fc: FeatureCollection) => {
  // get bounding box of all shapes
  const bounds = bbox(fc);
  const centroid = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2];
  const [latMin, latMax, lngMin, lngMax] = [
    bounds[1],
    bounds[3],
    bounds[0],
    bounds[2],
  ];
  const zoom = bboxToZoom([latMin, latMax, lngMin, lngMax]);

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
