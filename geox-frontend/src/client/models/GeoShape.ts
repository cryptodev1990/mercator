/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Feature } from './Feature';

/**
 * Metadata about a shape.
 */
export type GeoShape = {
    uuid: string;
    /**
     * Name of the shape
     */
    name?: string;
    namespace_id?: string;
    /**
     * Properties of the shape
     */
    properties: any;
    /**
     * Date and time of creation
     */
    created_at: string;
    /**
     * Date and time of most recent updater
     */
    updated_at: string;
    geojson: Feature;
};

