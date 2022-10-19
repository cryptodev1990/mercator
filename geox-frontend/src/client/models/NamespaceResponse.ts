/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { GeoShapeMetadata } from './GeoShapeMetadata';

/**
 * Response in get namespaces.
 */
export type NamespaceResponse = {
    id: string;
    name: string;
    slug: string;
    properties: any;
    organization_id: string;
    created_at: string;
    updated_at: string;
    is_default: boolean;
    /**
     *
     * List of shape metadata of shapes in the namespace.
     * None means that shape metadata wasn't requested.
     * An empty list means that there are no shapes.
     */
    shapes?: Array<GeoShapeMetadata>;
};

