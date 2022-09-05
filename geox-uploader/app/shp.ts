import { Proj4Projection } from "@math.gl/proj4";
import { parse, parseInBatches } from "@loaders.gl/core";
import { binaryToGeometry, transformGeoJsonCoords } from "@loaders.gl/gis";
import { SHPLoader, DBFLoader } from "@loaders.gl/shapefile";

const {
  parseShx,
} = require("@loaders.gl/shapefile/dist/lib/parsers/parse-shx");
const {
  zipBatchIterators,
} = require("@loaders.gl/shapefile/dist/lib/streaming/zip-batch-iterators");

export async function* parseShapefileInBatches(
  asyncIterator: AsyncIterable<ArrayBuffer> | Iterable<ArrayBuffer>,
  shx: any,
  dbf: any,
  cpg: any,
  prj: any,
  options?: any
): AsyncIterable<any> {
  const { reproject = false, _targetCrs = "WGS84" } = options?.gis || {};

  // parse geometries
  // @ts-ignore context must be defined
  const shapeIterable: any = await parseInBatches(
    asyncIterator,
    SHPLoader,
    options
  );

  // parse properties
  let propertyIterable: any;
  propertyIterable = await parseInBatches(dbf, DBFLoader, {
    ...options,
    dbf: { encoding: cpg || "latin1" },
  });

  // When `options.metadata` is `true`, there's an extra initial `metadata`
  // object before the iterator starts. zipBatchIterators expects to receive
  // batches of Array objects, and will fail with non-iterable batches, so it's
  // important to skip over the first batch.
  let shapeHeader = (await shapeIterable.next()).value;
  if (shapeHeader && shapeHeader.batchType === "metadata") {
    shapeHeader = (await shapeIterable.next()).value;
  }

  let dbfHeader: { batchType?: string } = {};
  if (propertyIterable) {
    dbfHeader = (await propertyIterable.next()).value;
    if (dbfHeader && dbfHeader.batchType === "metadata") {
      dbfHeader = (await propertyIterable.next()).value;
    }
  }

  let iterator: any;
  if (propertyIterable) {
    iterator = zipBatchIterators(shapeIterable, propertyIterable);
  } else {
    iterator = shapeIterable;
  }

  for await (const item of iterator) {
    let geometries: any;
    let properties: any;
    if (!propertyIterable) {
      geometries = item;
    } else {
      [geometries, properties] = item;
    }

    const geojsonGeometries = parseGeometries(geometries);
    let features = joinProperties(geojsonGeometries, properties);
    if (reproject) {
      // @ts-ignore
      features = reprojectFeatures(features, prj, _targetCrs);
    }
    yield {
      encoding: cpg,
      prj,
      shx,
      header: shapeHeader,
      data: features,
    };
  }
}

/**
 * Parse shapefile
 *
 * @param arrayBuffer
 * @param options
 * @param context
 * @returns output of shapefile
 */
async function parseShapefile(
  arrayBuffer: ArrayBuffer,
  shx: any,
  cpg: any,
  prj: any,
  dbf: ArrayBuffer,
  options?: any,
  context?: any
): Promise<any> {
  const { reproject = false, _targetCrs = "WGS84" } = options?.gis || {};

  // parse geometries
  // @ts-ignore context must be defined
  const { header, geometries } = await parse(arrayBuffer, SHPLoader, options); // {shp: shx}

  const geojsonGeometries = parseGeometries(geometries);

  // parse properties
  let properties = [];

  properties = await parse(dbf, DBFLoader, {
    dbf: { encoding: cpg || "latin1" },
  });

  let features = joinProperties(geojsonGeometries, properties);
  if (reproject) {
    features = reprojectFeatures(features, prj, _targetCrs);
  }

  return {
    encoding: cpg,
    prj,
    shx,
    header,
    data: features,
  };
}

/**
 * Parse geometries
 *
 * @param geometries
 * @returns geometries as an array
 */
function parseGeometries(geometries: any[]): any[] {
  const geojsonGeometries: any[] = [];
  for (const geom of geometries) {
    geojsonGeometries.push(binaryToGeometry(geom));
  }
  return geojsonGeometries;
}

/**
 * Join properties and geometries into features
 *
 * @param geometries [description]
 * @param  properties [description]
 * @return [description]
 */
function joinProperties(geometries: object[], properties: object[]): any[] {
  const features: any[] = [];
  for (let i = 0; i < geometries.length; i++) {
    const geometry = geometries[i];
    const feature: any = {
      type: "Feature",
      geometry,
      // properties can be undefined if dbfResponse above was empty
      properties: (properties && properties[i]) || {},
    };
    features.push(feature);
  }

  return features;
}

/**
 * Reproject GeoJSON features to output CRS
 *
 * @param features parsed GeoJSON features
 * @param sourceCrs source coordinate reference system
 * @param targetCrs †arget coordinate reference system
 * @return Reprojected Features
 */
function reprojectFeatures(
  features: any,
  sourceCrs?: string,
  targetCrs?: string
): any[] {
  if (!sourceCrs && !targetCrs) {
    return features;
  }

  const projection = new Proj4Projection({
    from: sourceCrs || "WGS84",
    to: targetCrs || "WGS84",
  });
  return transformGeoJsonCoords(features, (coord) => projection.project(coord));
}

export async function handleShapefile(files: any): Promise<any> {
  let shx, cpg, prj, shp, dbf;
  for (const f in files) {
    const data = files[f];
    const ext = f.split(".").pop();
    if (ext === "shp") {
      shp = data;
    } else if (ext === "shx") {
      shx = await parseShx(data);
    } else if (ext === "dbf") {
      dbf = data;
    } else if (ext === "prj") {
      prj = new TextDecoder().decode(data);
    } else if (ext === "cpg") {
      cpg = new TextDecoder().decode(data);
    }
  }
  return parseShapefile(shp, shx, cpg, prj, dbf);
}
