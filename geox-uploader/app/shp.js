"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __await = (this && this.__await) || function (v) { return this instanceof __await ? (this.v = v, this) : new __await(v); }
var __asyncValues = (this && this.__asyncValues) || function (o) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var m = o[Symbol.asyncIterator], i;
    return m ? m.call(o) : (o = typeof __values === "function" ? __values(o) : o[Symbol.iterator](), i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i);
    function verb(n) { i[n] = o[n] && function (v) { return new Promise(function (resolve, reject) { v = o[n](v), settle(resolve, reject, v.done, v.value); }); }; }
    function settle(resolve, reject, d, v) { Promise.resolve(v).then(function(v) { resolve({ value: v, done: d }); }, reject); }
};
var __asyncGenerator = (this && this.__asyncGenerator) || function (thisArg, _arguments, generator) {
    if (!Symbol.asyncIterator) throw new TypeError("Symbol.asyncIterator is not defined.");
    var g = generator.apply(thisArg, _arguments || []), i, q = [];
    return i = {}, verb("next"), verb("throw"), verb("return"), i[Symbol.asyncIterator] = function () { return this; }, i;
    function verb(n) { if (g[n]) i[n] = function (v) { return new Promise(function (a, b) { q.push([n, v, a, b]) > 1 || resume(n, v); }); }; }
    function resume(n, v) { try { step(g[n](v)); } catch (e) { settle(q[0][3], e); } }
    function step(r) { r.value instanceof __await ? Promise.resolve(r.value.v).then(fulfill, reject) : settle(q[0][2], r); }
    function fulfill(value) { resume("next", value); }
    function reject(value) { resume("throw", value); }
    function settle(f, v) { if (f(v), q.shift(), q.length) resume(q[0][0], q[0][1]); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleShapefile = exports.parseShapefileInBatches = void 0;
const proj4_1 = require("@math.gl/proj4");
const core_1 = require("@loaders.gl/core");
const gis_1 = require("@loaders.gl/gis");
const shapefile_1 = require("@loaders.gl/shapefile");
const { parseShx, } = require("@loaders.gl/shapefile/dist/lib/parsers/parse-shx");
const { parseSHP, } = require("@loaders.gl/shapefile/dist/lib/parsers/parse-shp");
const { parseDBF, } = require("@loaders.gl/shapefile/dist/lib/parsers/parse-dbf");
const { zipBatchIterators, } = require("@loaders.gl/shapefile/dist/lib/streaming/zip-batch-iterators");
function parseShapefileInBatches(asyncIterator, shx, dbf, cpg, prj, options) {
    return __asyncGenerator(this, arguments, function* parseShapefileInBatches_1() {
        var e_1, _a;
        const { reproject = false, _targetCrs = "WGS84" } = (options === null || options === void 0 ? void 0 : options.gis) || {};
        // parse geometries
        // @ts-ignore context must be defined
        const shapeIterable = yield __await((0, core_1.parseInBatches)(asyncIterator, shapefile_1.SHPLoader, options));
        // parse properties
        let propertyIterable;
        propertyIterable = yield __await((0, core_1.parseInBatches)(dbf, shapefile_1.DBFLoader, Object.assign(Object.assign({}, options), { dbf: { encoding: cpg || "latin1" } })));
        // When `options.metadata` is `true`, there's an extra initial `metadata`
        // object before the iterator starts. zipBatchIterators expects to receive
        // batches of Array objects, and will fail with non-iterable batches, so it's
        // important to skip over the first batch.
        let shapeHeader = (yield __await(shapeIterable.next())).value;
        if (shapeHeader && shapeHeader.batchType === "metadata") {
            shapeHeader = (yield __await(shapeIterable.next())).value;
        }
        let dbfHeader = {};
        if (propertyIterable) {
            dbfHeader = (yield __await(propertyIterable.next())).value;
            if (dbfHeader && dbfHeader.batchType === "metadata") {
                dbfHeader = (yield __await(propertyIterable.next())).value;
            }
        }
        let iterator;
        if (propertyIterable) {
            iterator = zipBatchIterators(shapeIterable, propertyIterable);
        }
        else {
            iterator = shapeIterable;
        }
        try {
            for (var iterator_1 = __asyncValues(iterator), iterator_1_1; iterator_1_1 = yield __await(iterator_1.next()), !iterator_1_1.done;) {
                const item = iterator_1_1.value;
                let geometries;
                let properties;
                if (!propertyIterable) {
                    geometries = item;
                }
                else {
                    [geometries, properties] = item;
                }
                const geojsonGeometries = parseGeometries(geometries);
                let features = joinProperties(geojsonGeometries, properties);
                if (reproject) {
                    // @ts-ignore
                    features = reprojectFeatures(features, prj, _targetCrs);
                }
                yield yield __await({
                    encoding: cpg,
                    prj,
                    shx,
                    header: shapeHeader,
                    data: features,
                });
            }
        }
        catch (e_1_1) { e_1 = { error: e_1_1 }; }
        finally {
            try {
                if (iterator_1_1 && !iterator_1_1.done && (_a = iterator_1.return)) yield __await(_a.call(iterator_1));
            }
            finally { if (e_1) throw e_1.error; }
        }
    });
}
exports.parseShapefileInBatches = parseShapefileInBatches;
/**
 * Parse shapefile
 *
 * @param arrayBuffer
 * @param options
 * @param context
 * @returns output of shapefile
 */
function parseShapefile(arrayBuffer, shx, cpg, prj, dbf, options, context) {
    return __awaiter(this, void 0, void 0, function* () {
        const { reproject = false, _targetCrs = "WGS84" } = (options === null || options === void 0 ? void 0 : options.gis) || {};
        // parse geometries
        // @ts-ignore context must be defined
        const { header, geometries } = yield (0, core_1.parse)(arrayBuffer, shapefile_1.SHPLoader, options); // {shp: shx}
        const geojsonGeometries = parseGeometries(geometries);
        // parse properties
        let properties = [];
        properties = yield (0, core_1.parse)(dbf, shapefile_1.DBFLoader, {
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
    });
}
/**
 * Parse geometries
 *
 * @param geometries
 * @returns geometries as an array
 */
function parseGeometries(geometries) {
    const geojsonGeometries = [];
    for (const geom of geometries) {
        geojsonGeometries.push((0, gis_1.binaryToGeometry)(geom));
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
function joinProperties(geometries, properties) {
    const features = [];
    for (let i = 0; i < geometries.length; i++) {
        const geometry = geometries[i];
        const feature = {
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
function reprojectFeatures(features, sourceCrs, targetCrs) {
    if (!sourceCrs && !targetCrs) {
        return features;
    }
    const projection = new proj4_1.Proj4Projection({
        from: sourceCrs || "WGS84",
        to: targetCrs || "WGS84",
    });
    return (0, gis_1.transformGeoJsonCoords)(features, (coord) => projection.project(coord));
}
function handleShapefile(files) {
    return __awaiter(this, void 0, void 0, function* () {
        let shx, cpg, prj, shp, dbf;
        for (const f in files) {
            const data = files[f];
            const ext = f.split(".").pop();
            if (ext === "shp") {
                shp = data;
            }
            else if (ext === "shx") {
                shx = yield parseShx(data);
            }
            else if (ext === "dbf") {
                dbf = data;
            }
            else if (ext === "prj") {
                prj = new TextDecoder().decode(data);
            }
            else if (ext === "cpg") {
                cpg = new TextDecoder().decode(data);
            }
        }
        return parseShapefile(shp, shx, cpg, prj, dbf);
    });
}
exports.handleShapefile = handleShapefile;
