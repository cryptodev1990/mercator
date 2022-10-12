/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Feature } from './Feature';

export type GeoShapeUpdate = {
    uuid?: string;
    name?: string;
    geojson?: Feature;
    properties?: any;
    /**
     * The namespace id
     */
    namespace?: string;
    should_delete?: boolean;
};

