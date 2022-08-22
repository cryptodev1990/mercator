/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DbCredentialCreate } from "../models/DbCredentialCreate";
import type { DbCredentialUpdate } from "../models/DbCredentialUpdate";
import type { GetAllConnectionsType } from "../models/GetAllConnectionsType";
import type { PublicDbCredential } from "../models/PublicDbCredential";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class DbConfigService {
  /**
   * Read Db Conns
   * Read all connections. Requires that the user be in the same organization as the connection.
   * @param type
   * @returns PublicDbCredential Successful Response
   * @throws ApiError
   */
  public static readDbConnsDbConfigConnectionsGet(
    type?: GetAllConnectionsType
  ): CancelablePromise<Array<PublicDbCredential>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/db_config/connections",
      query: {
        type: type,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Create Db Conn
   * Creates a database connection
   * @param requestBody
   * @returns PublicDbCredential Successful Response
   * @throws ApiError
   */
  public static createDbConnDbConfigConnectionsPost(
    requestBody: DbCredentialCreate
  ): CancelablePromise<PublicDbCredential> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/db_config/connections",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Read Db Conn
   * Read a single connection by UUID. Requires that the user be in the same organization as the connection.
   * @param uuid
   * @returns PublicDbCredential Successful Response
   * @throws ApiError
   */
  public static readDbConnDbConfigConnectionsUuidGet(
    uuid: string
  ): CancelablePromise<PublicDbCredential> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/db_config/connections/{uuid}",
      path: {
        uuid: uuid,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Delete Db Conn
   * Deletes a database connection
   * @param uuid
   * @returns any Successful Response
   * @throws ApiError
   */
  public static deleteDbConnDbConfigConnectionsUuidDelete(
    uuid: string
  ): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/db_config/connections/{uuid}",
      path: {
        uuid: uuid,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Update Db Conn
   * Updates a single db connection
   * @param requestBody
   * @returns PublicDbCredential Successful Response
   * @throws ApiError
   */
  public static updateDbConnDbConfigConnectionsUuidPatch(
    requestBody: DbCredentialUpdate
  ): CancelablePromise<PublicDbCredential> {
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/db_config/connections/{uuid}",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
