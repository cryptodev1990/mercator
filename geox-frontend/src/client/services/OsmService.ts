/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Feature } from '../models/Feature';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class OsmService {

    /**
     * Get Shapes From Osm
     * Get shapes from OSM by amenity
     * @param query
     * @param geographicReference
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getShapesFromOsmOsmGet(
        query: string,
        geographicReference: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/osm',
            query: {
                'query': query,
                'geographic_reference': geographicReference,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Roads By Bounding Box
     * @param xmin
     * @param ymin
     * @param xmax
     * @param ymax
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getRoadsByBoundingBoxOsmWaysGet(
        xmin: number,
        ymin: number,
        xmax: number,
        ymax: number,
        requestBody: Feature,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/osm/ways/',
            query: {
                'xmin': xmin,
                'ymin': ymin,
                'xmax': xmax,
                'ymax': ymax,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Isochrone
     * Get shapes from OSM by amenity
     * @param timeInMinutes
     * @param profile
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static isochroneOsmIsochroneGet(
        timeInMinutes: number,
        profile: string,
        requestBody: Array<Array<any>>,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/osm/isochrone',
            query: {
                'time_in_minutes': timeInMinutes,
                'profile': profile,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
