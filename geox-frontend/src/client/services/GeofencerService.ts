/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CeleryTaskResponse } from "../../client/models/CeleryTaskResponse";
import type { CeleryTaskResult } from "../../client/models/CeleryTaskResult";
import type { Feature } from "../../client/models/Feature";
import type { GeometryOperation } from "../../client/models/GeometryOperation";
import type { GeoShape } from "../../client/models/GeoShape";
import type { GeoShapeCreate } from "../../client/models/GeoShapeCreate";
import type { GeoShapeMetadata } from "../models/GeoShapeMetadata";
import type { GeoShapeUpdate } from "../../client/models/GeoShapeUpdate";
import type { GetAllShapesRequestType } from "../../client/models/GetAllShapesRequestType";
import type { LineString } from "../../client/models/LineString";
import type { Point } from "../../client/models/Point";
import type { Polygon } from "../../client/models/Polygon";
import type { ShapeCountResponse } from "../../client/models/ShapeCountResponse";
import type { TileMatrixSetNames } from "../../client/models/TileMatrixSetNames";

import type { CancelablePromise } from "../../client/core/CancelablePromise";
import { OpenAPI } from "../../client/core/OpenAPI";
import { request as __request } from "../../client/core/request";

export class GeofencerService {
  /**
   * Get All Shapes
   * Read shapes.
   * @param rtype
   * @param offset
   * @param limit
   * @returns GeoShape Successful Response
   * @throws ApiError
   */
  public static getAllShapesGeofencerShapesGet(
    rtype: GetAllShapesRequestType,
    offset?: number,
    limit: number = 300
  ): CancelablePromise<Array<GeoShape>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shapes",
      query: {
        rtype: rtype,
        offset: offset,
        limit: limit,
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
   * Get Shape
   * Read a shape.
   * @param uuid
   * @param responses
   * @returns GeoShape Successful Response
   * @throws ApiError
   */
  public static getShapeGeofencerShapesUuidGet(
    uuid: string,
    responses?: any
  ): CancelablePromise<GeoShape> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shapes/{uuid}",
      path: {
        uuid: uuid,
      },
      query: {
        responses: responses,
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
    requestBody: GeoShapeUpdate
  ): CancelablePromise<GeoShape> {
    return __request(OpenAPI, {
      method: "PUT",
      url: "/geofencer/shapes/{uuid}",
      body: requestBody,
      mediaType: "application/json",
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
    requestBody: Array<GeoShapeCreate>
  ): CancelablePromise<ShapeCountResponse> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/geofencer/shapes/bulk",
      body: requestBody,
      mediaType: "application/json",
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
   * Shapes Export
   * Export shapes to S3.
   *
   * This is an async task. Use `/tasks/results/{task_id}` to retrieve the status and results.
   * @returns CeleryTaskResponse Successful Response
   * @throws ApiError
   */
  public static shapesExportShapesExportPost(): CancelablePromise<CeleryTaskResponse> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/shapes/export",
      errors: {
        403: `Data export not enabled for this account`,
        501: `Data export not supported on the server.`,
      },
    });
  }

  /**
   * Get Shape Metadata By Bounding Box
   * Get shape metadata by bounding box.
   * @param minX
   * @param minY
   * @param maxX
   * @param maxY
   * @param limit
   * @param offset
   * @returns GeoShapeMetadata Successful Response
   * @throws ApiError
   */
  public static getShapeMetadataByBoundingBoxGeofencerShapeMetadataBboxGet(
    minX: number,
    minY: number,
    maxX: number,
    maxY: number,
    limit: number = 25,
    offset?: number
  ): CancelablePromise<Array<GeoShapeMetadata>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shape-metadata/bbox",
      query: {
        min_x: minX,
        min_y: minY,
        max_x: maxX,
        max_y: maxY,
        limit: limit,
        offset: offset,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get Shape Metadata Matching Search
   * Get shape metadata by bounding box.
   * @param query
   * @param limit
   * @param offset
   * @returns GeoShapeMetadata Successful Response
   * @throws ApiError
   */
  public static getShapeMetadataMatchingSearchGeofencerShapeMetadataSearchGet(
    query: string,
    limit: number = 25,
    offset?: number
  ): CancelablePromise<Array<GeoShapeMetadata>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shape-metadata/search",
      query: {
        query: query,
        limit: limit,
        offset: offset,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Get All Shape Metadata
   * Get all shape metadata with pagination
   * @param limit
   * @param offset
   * @returns GeoShapeMetadata Successful Response
   * @throws ApiError
   */
  public static getAllShapeMetadataGeofencerShapeMetadataGet(
    limit: number = 25,
    offset?: number
  ): CancelablePromise<Array<GeoShapeMetadata>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shape-metadata",
      query: {
        limit: limit,
        offset: offset,
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
   * @deprecated
   * Copy Shapes
   * Export shapes to S3.
   *
   * This is an async task. Use `/tasks/results/{task_id}` to retieve the status and results.
   *
   * Exports all shapes in the user's organization to Snowflake, if the user's account is
   * enabled for shape export, and the user has provided Snowflake account information for sharing.
   *
   * Use `POST /shapes/export` instead.
   * @returns CeleryTaskResponse Successful Response
   * @throws ApiError
   */
  public static copyShapesTasksCopyShapesPost(): CancelablePromise<CeleryTaskResponse> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/tasks/copy_shapes",
      errors: {
        403: `Data export not enabled for this account`,
        501: `Shape export is not configured`,
      },
    });
  }

  /**
   * Get Shape Tile
   * Get a tile of shape
   * @param z Tiles's zoom level
   * @param x Tiles's column
   * @param y Tiles's row
   * @param layer Layer Name
   * @param tileMatrixSetId TileMatrixSet Name (default: 'WebMercatorQuad')
   * @returns any Successful Response
   * @throws ApiError
   */
  public static getShapeTileBacksplashLayerZXYGet(
    z: number,
    x: number,
    y: number,
    layer: string,
    tileMatrixSetId?: TileMatrixSetNames
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/backsplash/{layer}/{z}/{x}/{y}",
      path: {
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
