import { bbox } from "@turf/turf";
import { Feature } from "../client";

export function findIndex(uuid: string, collection: any): number {
  /**
   * Find index of a UUID in a collection of elements that all have UUIDs
   */
  if (collection === undefined) {
    return -1;
  }
  for (let i = 0; i < collection.length; i++) {
    if (collection[i].uuid === uuid) {
      return i;
    }
  }
  return -1;
}

export function lngToTile(lon: number, zoom: number) {
  return Math.floor(((lon + 180) / 360) * Math.pow(2, zoom));
}

export function latToTile(lat: number, zoom: number) {
  return Math.floor(
    ((1 -
      Math.log(
        Math.tan((lat * Math.PI) / 180) + 1 / Math.cos((lat * Math.PI) / 180)
      ) /
        Math.PI) /
      2) *
      Math.pow(2, zoom)
  );
}

export function getAllTilesBetween(
  zoom: number,
  x1: number,
  y1: number,
  x2: number,
  y2: number
) {
  const tiles: { x: number; y: number; z: number }[] = [];
  for (let x = x1; x <= x2; x++) {
    for (let y = y1; y <= y2; y++) {
      tiles.push({ x, y, z: zoom });
    }
  }
  return tiles;
}

export function tilesForGeoJson(geojson: Feature, zoom: number): string[] {
  zoom = Math.floor(zoom);
  const bx = bbox(geojson);
  const x1 = lngToTile(bx[0], zoom);
  const y1 = latToTile(bx[3], zoom);
  const x2 = lngToTile(bx[2], zoom);
  const y2 = latToTile(bx[1], zoom);
  const tileList = getAllTilesBetween(zoom, x1, y1, x2, y2);
  const tl = tileList.map((t) => `${t.x}-${t.y}-${t.z}`);
  return tl;
}

export function debounceFn(cb: any, delay = 250) {
  let timeout: any;

  return (...args: any) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      cb(...args);
    }, delay);
  };
}
