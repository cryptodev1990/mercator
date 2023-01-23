/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CeleryTaskResponse } from "../models/CeleryTaskResponse";
import type { CeleryTaskResult } from "../models/CeleryTaskResult";
import type { Feature } from "../models/Feature";
import type { GeometryOperation } from "../models/GeometryOperation";
import type { GeoShape } from "../models/GeoShape";
import type { GeoShapeCreate } from "../models/GeoShapeCreate";
import type { GeoShapeMetadata } from "../models/GeoShapeMetadata";
import type { GeoShapeUpdate } from "../models/GeoShapeUpdate";
import type { LineString } from "../models/LineString";
import type { Point } from "../models/Point";
import type { Polygon } from "../models/Polygon";
import type { ShapeCountResponse } from "../models/ShapeCountResponse";
import type { TileMatrixSetNames } from "../models/TileMatrixSetNames";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";
import { ShapesBulkUploadOptions } from "features/geofence-map/types";

export class GeofencerService {
  /**
   * Get Status
   * Retrieve results of a task.
   * @param taskId
   * @returns CeleryTaskResult Successful Response
   * @throws ApiError
   */
  public static getStatusGeofencerShapesExportTaskIdGet(
    taskId: string
  ): CancelablePromise<CeleryTaskResult> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shapes/export/{task_id}",
      path: {
        task_id: taskId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Shapes Export
   * Export shapes to S3.
   *
   * This is an async task. Use `/tasks/results/{task_id}` to retrieve the status and results.
   * @returns CeleryTaskResponse Successful Response
   * @throws ApiError
   */
  public static shapesExportGeofencerShapesExportPost(): CancelablePromise<CeleryTaskResponse> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/geofencer/shapes/export",
      errors: {
        501: `Data export not supported on the server`,
      },
    });
  }

  /**
   * Bulk Create Shapes
   * Create multiple shapes.
   * @param requestBody
   * @param namespace
   * @param asList
   * @returns any Successful Response
   * @throws ApiError
   */
  public static bulkCreateShapesGeofencerShapesBulkPost(
    requestBody: ShapesBulkUploadOptions,
    namespace?: string,
    asList = false
  ): CancelablePromise<ShapeCountResponse | Array<GeoShape>> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/geofencer/shapes/bulk",
      query: {
        namespace: namespace,
        as_list: asList,
      },
      body: requestBody.shapes,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
      onUploadProgress: requestBody.onUploadProgress,
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
    requestBody: Array<string>
  ): CancelablePromise<ShapeCountResponse> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/geofencer/shapes/bulk",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Get Shapes
   * Read shapes.
   *
   * Will return 200 even if no shapes match the query, including the case in which the
   * namespace does not exist.
   * @param namespace Only include shapes in the specified namespace given its UUID or name.
   * @param user If TRUE, then only return shapes of the requesting user.
   * @param rtype
   * @param offset
   * @param limit
   * @returns GeoShape Successful Response
   * @throws ApiError
   */
  public static getShapesGeofencerShapesGet(
    namespace?: string,
    user?: boolean,
    offset?: number,
    limit: number = 1000,
    shapeIds?: Array<string>,
    bbox?: Array<number>
  ): CancelablePromise<Array<GeoShape>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shapes",
      query: {
        namespace: namespace,
        user: user,
        offset: offset,
        limit: limit,
        id: shapeIds,
        bbox: bbox,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Post Shapes
   * Create a shape.
   * @param requestBody
   * @returns GeoShape Successful Response
   * @throws ApiError
   */
  public static postShapesGeofencerShapesPost(
    requestBody: GeoShapeCreate
  ): CancelablePromise<GeoShape> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/geofencer/shapes",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get Shape Count
   * Get shape count.
   * @returns ShapeCountResponse Successful Response
   * @throws ApiError
   */
  public static getShapeCountGeofencerShapesOpCountGet(): CancelablePromise<ShapeCountResponse> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shapes/op/count",
    });
  }

  /**
   * Get Shapes Containing Point
   * Get shapes containing a point.
   * @param lat
   * @param lng
   * @returns Feature Successful Response
   * @throws ApiError
   */
  public static getShapesContainingPointGeofencerShapesOpContainsGet(
    lat: number,
    lng: number
  ): CancelablePromise<Array<Feature>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shapes/op/contains",
      query: {
        lat: lat,
        lng: lng,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Get Shapes  Shape Id
   * Read a shape.
   * @param shapeId
   * @returns GeoShape Successful Response
   * @throws ApiError
   */
  public static getShapesShapeIdGeofencerShapesShapeIdGet(
    shapeId: string
  ): CancelablePromise<GeoShape> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shapes/{shape_id}",
      path: {
        shape_id: shapeId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Delete Shapes  Shape Id
   * Delete a shape.
   * @param shapeId
   * @returns void
   * @throws ApiError
   */
  public static deleteShapesShapeIdGeofencerShapesShapeIdDelete(
    shapeId: string
  ): CancelablePromise<void> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/geofencer/shapes/{shape_id}",
      path: {
        shape_id: shapeId,
      },
      errors: {
        404: `Shape does not exist`,
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Patch Shapes  Shape Id
   * Update a shape.
   * @param shapeId
   * @param requestBody
   * @returns GeoShape Successful Response
   * @throws ApiError
   */
  public static patchShapeById(
    shapeId: string,
    requestBody: GeoShapeUpdate
  ): CancelablePromise<GeoShape> {
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/geofencer/shapes/{shape_id}",
      path: {
        shape_id: shapeId,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        404: `Shape does not exist`,
        422: `Validation Error`,
      },
    });
  }

  /**
   * @deprecated
   *  Update Shapes  Shape Id
   * Update a shape.
   * @param requestBody
   * @returns GeoShape Successful Response
   * @throws ApiError
   */
  public static updateShapesShapeIdGeofencerShapesUuidPut(
    requestBody: GeoShapeUpdate
  ): CancelablePromise<GeoShape> {
    return __request(OpenAPI, {
      method: "PUT",
      url: "/geofencer/shapes/{uuid}",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        404: `Shape does not exist`,
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get Shapes By Operation
   * Get shapes by operation.
   * @param operation
   * @param requestBody
   * @returns Feature Successful Response
   * @throws ApiError
   */
  public static getShapesByOperationGeofencerShapesOpOperationPost(
    operation: GeometryOperation,
    requestBody: Point | Polygon | LineString
  ): CancelablePromise<Array<Feature>> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/geofencer/shapes/op/{operation}",
      path: {
        operation: operation,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        403: `Operation not enabled for this account`,
        422: `Validation Error`,
        501: `Operation not supported on the server.`,
      },
    });
  }

  /**
   *  Get Shape Metadata  Bbox
   * Get shape metadata by bounding box.
   * @param minX
   * @param minY
   * @param maxX
   * @param maxY
   * @param offset
   * @param limit
   * @returns GeoShapeMetadata Successful Response
   * @throws ApiError
   */
  public static getShapeMetadataBboxGeofencerShapeMetadataBboxGet(
    minX: number,
    minY: number,
    maxX: number,
    maxY: number,
    offset?: number,
    limit: number = 25
  ): CancelablePromise<Array<GeoShapeMetadata>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shape-metadata/bbox",
      query: {
        min_x: minX,
        min_y: minY,
        max_x: maxX,
        max_y: maxY,
        offset: offset,
        limit: limit,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Get Shape Metadata  Search
   * Get shape metadata by bounding box.
   * @param query
   * @param offset
   * @param limit
   * @returns GeoShapeMetadata Successful Response
   * @throws ApiError
   */
  public static getShapeMetadataSearchGeofencerShapeMetadataSearchGet(
    query: string,
    offset?: number,
    limit: number = 25
  ): CancelablePromise<Array<GeoShapeMetadata>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shape-metadata/search",
      query: {
        query: query,
        offset: offset,
        limit: limit,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Get Shape Metadata
   * Get all shape metadata with pagination.
   * @param offset
   * @param limit
   * @returns GeoShapeMetadata Successful Response
   * @throws ApiError
   */
  public static getShapeMetadataGeofencerShapeMetadataGet(
    offset?: number,
    limit: number = 25,
    user?: boolean,
    namespace?: string,
    shapeIds?: Array<string>,
    bbox?: Array<number>
  ): CancelablePromise<Array<GeoShapeMetadata>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shape-metadata",
      query: {
        offset: offset,
        limit: limit,
        user: user,
        namespace: namespace,
        id: shapeIds,
        bbox: bbox,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get Status
   * Retrieve results of a task.
   * @param taskId
   * @returns CeleryTaskResult Successful Response
   * @throws ApiError
   */
  public static getStatusTasksResultsTaskIdGet(
    taskId: string
  ): CancelablePromise<CeleryTaskResult> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/tasks/results/{task_id}",
      path: {
        task_id: taskId,
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
    word: string = "Hello"
  ): CancelablePromise<CeleryTaskResponse> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/tasks/test",
      query: {
        word: word,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get Shape Tile
   * Get a tile of shape
   *
   * Cache key is used to keep the same result for immutable functions
   * On each material change (create/update/delete) for shapes
   * we bump the cache ID
   * @param cacheKey
   * @param z Tiles's zoom level
   * @param x Tiles's column
   * @param y Tiles's row
   * @param layer Layer Name
   * @param tileMatrixSetId TileMatrixSet Name (default: 'WebMercatorQuad')
   * @returns any Successful Response
   * @throws ApiError
   */
  public static getShapeTileBacksplashLayerZXYCacheKeyGet(
    cacheKey: number,
    z: number,
    x: number,
    y: number,
    layer: string,
    tileMatrixSetId?: TileMatrixSetNames
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/backsplash/{layer}/{z}/{x}/{y}/{cache_key}",
      path: {
        cache_key: cacheKey,
        z: z,
        x: x,
        y: y,
        layer: layer,
      },
      query: {
        TileMatrixSetId: tileMatrixSetId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
