/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CeleryTaskResponse } from '../models/CeleryTaskResponse';
import type { CeleryTaskResult } from '../models/CeleryTaskResult';
import type { Feature } from '../models/Feature';
import type { GeoShape } from '../models/GeoShape';
import type { GeoShapeCreate } from '../models/GeoShapeCreate';
import type { GeoShapeUpdate } from '../models/GeoShapeUpdate';
import type { GetAllShapesRequestType } from '../models/GetAllShapesRequestType';
import type { ShapeCountResponse } from '../models/ShapeCountResponse';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GeofencerService {

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

    /**
     * Get All Shapes
     * Read shapes.
     * @param rtype
     * @returns GeoShape Successful Response
     * @throws ApiError
     */
    public static getAllShapesGeofencerShapesGet(
        rtype: GetAllShapesRequestType,
    ): CancelablePromise<Array<GeoShape>> {
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
     * Create a shape.
     * @param requestBody
     * @returns GeoShape Successful Response
     * @throws ApiError
     */
    public static createShapeGeofencerShapesPost(
        requestBody: GeoShapeCreate,
    ): CancelablePromise<GeoShape> {
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

    /**
     * Get Shape
     * Read a shape.
     * @param uuid
     * @returns GeoShape Successful Response
     * @throws ApiError
     */
    public static getShapeGeofencerShapesUuidGet(
        uuid: string,
    ): CancelablePromise<GeoShape> {
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
     * Update a shape.
     * @param requestBody
     * @returns GeoShape Successful Response
     * @throws ApiError
     */
    public static updateShapeGeofencerShapesUuidPut(
        requestBody: GeoShapeUpdate,
    ): CancelablePromise<GeoShape> {
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
     * Bulk Create Shapes
     * Create multiple shapes.
     * @param requestBody
     * @returns ShapeCountResponse Successful Response
     * @throws ApiError
     */
    public static bulkCreateShapesGeofencerShapesBulkPost(
        requestBody: Array<GeoShapeCreate>,
    ): CancelablePromise<ShapeCountResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/geofencer/shapes/bulk',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Bulk Delete Shapes
     * Create multiple shapes.
     * @param requestBody
     * @returns ShapeCountResponse Successful Response
     * @throws ApiError
     */
    public static bulkDeleteShapesGeofencerShapesBulkDelete(
        requestBody: Array<string>,
    ): CancelablePromise<ShapeCountResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/geofencer/shapes/bulk',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Status
     * Retrieve results of a market selection task.
     * @param taskId
     * @returns CeleryTaskResult Successful Response
     * @throws ApiError
     */
    public static getStatusTasksResultsTaskIdGet(
        taskId: string,
    ): CancelablePromise<CeleryTaskResult> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks/results/{task_id}',
            path: {
                'task_id': taskId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Run Test Celery
     * Run a test celery task.
     * @param word
     * @returns CeleryTaskResponse Successful Response
     * @throws ApiError
     */
    public static runTestCeleryTasksTestPost(
        word: string = 'Hello',
    ): CancelablePromise<CeleryTaskResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tasks/test',
            query: {
                'word': word,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Run Copy Task
     * Run a test celery task.
     * @returns CeleryTaskResponse Successful Response
     * @throws ApiError
     */
    public static runCopyTaskTasksCopyShapesPost(): CancelablePromise<CeleryTaskResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tasks/copy_shapes',
        });
    }

}
