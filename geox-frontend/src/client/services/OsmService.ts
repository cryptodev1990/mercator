/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class OsmService {
  /**
   * Get Shapes From Osm
   * Get shapes from OSM by amenity.
   * @param query
   * @param geographicReference
   * @returns any Successful Response
   * @throws ApiError
   */
  public static getShapesFromOsmOsmGet(
    query: string,
    geographicReference: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/osm",
      query: {
        query: query,
        geographic_reference: geographicReference,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
