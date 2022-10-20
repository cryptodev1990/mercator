/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Feature } from './Feature';
import type { Point } from "./Point";
import type { MultiPoint } from "./MultiPoint";
import type { LineString } from "./LineString";
import type { MultiLineString } from "./MultiLineString";
import type { Polygon } from "./Polygon";
import type { MultiPolygon } from "./MultiPolygon";
import type { GeometryCollection } from "./GeometryCollection";

export type GeoShapeUpdate = {
    uuid?: string;
    name?: string;
    geojson?: Feature;
    properties?: any;
    namespace?: string;
    geometry?: (Point | MultiPoint | LineString | MultiLineString | Polygon | MultiPolygon | GeometryCollection);
};

