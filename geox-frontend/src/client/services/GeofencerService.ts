/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GeoShape } from "../models/GeoShape";
import type { GeoShapeCreate } from "../models/GeoShapeCreate";
import type { GeoShapeUpdate } from "../models/GeoShapeUpdate";
import type { GetAllShapesRequestType } from "../models/GetAllShapesRequestType";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class GeofencerService {
  /**
   * Get Shapes From Osm By Amenity
   * Get shapes from OSM by amenity
   * @returns any Successful Response
   * @throws ApiError
   */
  public static getShapesFromOsmByAmenityOsmDemoGet(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/osm/demo",
    });
  }

  /**
   * Get Shape
   * @param uuid
   * @returns GeoShape Successful Response
   * @throws ApiError
   */
  public static getShapeGeofencerShapesUuidGet(
    uuid: string
  ): CancelablePromise<GeoShape> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shapes/{uuid}",
      path: {
        uuid: uuid,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Update Shape
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
   * Get All Shapes
   * @param rtype
   * @returns GeoShape Successful Response
   * @throws ApiError
   */
  public static getAllShapesGeofencerShapesGet(
    rtype: GetAllShapesRequestType
  ): CancelablePromise<Array<GeoShape>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/shapes",
      query: {
        rtype: rtype,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Create Shape
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
   * Bulk Soft Delete Shapes
   * @param requestBody
   * @returns any Successful Response
   * @throws ApiError
   */
  public static bulkSoftDeleteShapesGeofencerShapesDelete(
    requestBody: Array<string>
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/geofencer/shapes",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Bulk Create Shapes
   * @param requestBody
   * @returns any Successful Response
   * @throws ApiError
   */
  public static bulkCreateShapesGeofencerShapesBulkPost(
    requestBody: Array<GeoShapeCreate>
  ): CancelablePromise<any> {
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
}
