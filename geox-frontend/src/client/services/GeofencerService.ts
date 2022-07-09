/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GeoShapeCreate } from '../models/GeoShapeCreate';
import type { GeoShapeUpdate } from '../models/GeoShapeUpdate';
import type { GetAllShapesRequestType } from '../models/GetAllShapesRequestType';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GeofencerService {

    /**
     * Get Shape
     * @param uuid
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getShapeGeofencerShapesUuidGet(
        uuid: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/geofencer/shapes/{uuid}',
            path: {
                'uuid': uuid,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Update Shape
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static updateShapeGeofencerShapesUuidPut(
        requestBody: GeoShapeUpdate,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/geofencer/shapes/{uuid}',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get All Shapes
     * @param rtype
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAllShapesGeofencerShapesGet(
        rtype: GetAllShapesRequestType,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/geofencer/shapes',
            query: {
                'rtype': rtype,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Create Shape
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static createShapeGeofencerShapesPost(
        requestBody: GeoShapeCreate,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/geofencer/shapes',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
