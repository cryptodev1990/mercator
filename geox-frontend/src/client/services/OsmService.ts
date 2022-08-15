/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class OsmService {

    /**
     * Get Shapes From Osm By Amenity
     * Get shapes from OSM by amenity
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getShapesFromOsmByAmenityOsmDemoGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/osm/demo',
        });
    }

}
