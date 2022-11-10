/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GeoShapeMetadata } from "../models/GeoShapeMetadata";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class ShapeMetadataService {
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
}
