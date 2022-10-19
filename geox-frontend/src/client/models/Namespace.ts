/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GeoShapeMetadata } from './GeoShapeMetadata';

/**
 * Namespace data.
 */
export type Namespace = {
    id: string;
    name: string;
    slug: string;
    properties: any;
    organization_id: string;
    created_at: string;
    updated_at: string;
    is_default: boolean;
    shapes?: Array<GeoShapeMetadata>;
};

