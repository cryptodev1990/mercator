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

export function tilesForGeoJson(geojson: any, zoom: number) {
  const tiles: { x: number; y: number; z: number }[] = [];
  for (const feature of geojson.features) {
    for (const coord of feature.geometry.coordinates) {
      const tile = {
        x: lngToTile(coord[0], zoom),
        y: latToTile(coord[1], zoom),
        z: zoom,
      };
      if (!tiles.find((t) => t.x === tile.x && t.y === tile.y)) {
        tiles.push(tile);
      }
    }
  }
  return tiles;
}
