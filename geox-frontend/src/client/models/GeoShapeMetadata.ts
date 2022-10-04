/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Metadata about a shape.
 */
export type GeoShapeMetadata = {
    /**
     * Unique identifier for the shape
     */
    uuid: string;
    /**
     * Name of the shape
     */
    name?: string;
    /**
     * Properties of the shape
     */
    properties?: any;
    /**
     * Date and time of creation
     */
    created_at: string;
    /**
     * Date and time of most recent updater
     */
    updated_at?: string;
};

