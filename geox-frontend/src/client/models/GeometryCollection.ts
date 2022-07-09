/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { LineString } from './LineString';
import type { MultiLineString } from './MultiLineString';
import type { MultiPoint } from './MultiPoint';
import type { MultiPolygon } from './MultiPolygon';
import type { Point } from './Point';
import type { Polygon } from './Polygon';

/**
 * GeometryCollection Model
 */
export type GeometryCollection = {
    type?: string;
    geometries: Array<(Point | MultiPoint | LineString | MultiLineString | Polygon | MultiPolygon)>;
};

