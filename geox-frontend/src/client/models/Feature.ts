/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GeometryCollection } from './GeometryCollection';
import type { LineString } from './LineString';
import type { MultiLineString } from './MultiLineString';
import type { MultiPoint } from './MultiPoint';
import type { MultiPolygon } from './MultiPolygon';
import type { Point } from './Point';
import type { Polygon } from './Polygon';

/**
 * Feature Model
 */
export type Feature = {
    type?: string;
    geometry?: (Point | MultiPoint | LineString | MultiLineString | Polygon | MultiPolygon | GeometryCollection);
    properties?: any;
    id?: string;
    bbox?: Array<Number>;
};

