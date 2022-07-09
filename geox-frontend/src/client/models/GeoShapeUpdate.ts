/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Feature } from './Feature';

export type GeoShapeUpdate = {
    /**
     * Unique identifier for the shape
     */
    uuid: string;
    name?: string;
    geojson?: Feature;
    /**
     * If true, deletes the shape
     */
    should_delete?: boolean;
};

