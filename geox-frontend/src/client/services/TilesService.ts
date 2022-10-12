/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TileMatrixSetNames } from "../models/TileMatrixSetNames";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class TilesService {
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
