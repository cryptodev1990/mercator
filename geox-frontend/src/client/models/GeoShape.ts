/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Feature } from './Feature';

export type GeoShape = {
    /**
     * Name of the shape
     */
    name?: string;
    /**
     * GeoJSON representation of the shape
     */
    geojson: Feature;
    /**
     * Unique identifier for the shape
     */
    uuid: string;
    /**
     * User ID of the creator
     */
    created_by_user_id: number;
    /**
     * Date and time of creation
     */
    created_at: string;
    /**
     * User ID of the most recent updater
     */
    updated_by_user_id?: number;
    /**
     * Date and time of most recent updater
     */
    updated_at?: string;
};

