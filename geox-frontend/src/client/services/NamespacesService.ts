/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Namespace } from "../models/Namespace";
import type { NamespaceCreate } from "../models/NamespaceCreate";
import type { NamespaceResponse } from "../models/NamespaceResponse";
import type { NamespaceUpdate } from "../models/NamespaceUpdate";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class NamespacesService {
  /**
   *  Get Namespaces
   * Return namespaces available to the user.
   * @param id
   * @param name
   * @returns NamespaceResponse Successful Response
   * @throws ApiError
   */
  public static getNamespacesGeofencerNamespacesGet(
    id?: string,
    name?: string
  ): CancelablePromise<Array<NamespaceResponse>> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/namespaces",
      query: {
        id: id,
        name: name,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Post Namespaces
   * Create a new namespace.
   * @param requestBody
   * @returns Namespace Successful Response
   * @throws ApiError
   */
  public static postNamespacesGeofencerNamespacesPost(
    requestBody: NamespaceCreate
  ): CancelablePromise<Namespace> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/geofencer/namespaces",
      body: requestBody,
      mediaType: "application/json",
      errors: {
        404: `Namespace does not exist`,
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Get Namespaces  Namespace Id
   * Return a namespace.
   * @param namespaceId
   * @returns NamespaceResponse Successful Response
   * @throws ApiError
   */
  public static getNamespacesNamespaceIdGeofencerNamespacesNamespaceIdGet(
    namespaceId: string
  ): CancelablePromise<NamespaceResponse> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/geofencer/namespaces/{namespace_id}",
      path: {
        namespace_id: namespaceId,
      },
      errors: {
        409: `Namespace exists`,
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Delete Namespaces
   * Return namespaces available to the user.
   *
   * - 204: Success with no content
   * @param namespaceId
   * @returns void
   * @throws ApiError
   */
  public static deleteNamespacesGeofencerNamespacesNamespaceIdDelete(
    namespaceId: string
  ): CancelablePromise<void> {
    return __request(OpenAPI, {
      method: "DELETE",
      url: "/geofencer/namespaces/{namespace_id}",
      path: {
        namespace_id: namespaceId,
      },
      errors: {
        409: `Namespace exists`,
        422: `Validation Error`,
      },
    });
  }

  /**
   *  Patch Namespaces
   * Return namespaces available to the user.
   * @param namespaceId
   * @param requestBody
   * @returns NamespaceResponse Successful Response
   * @throws ApiError
   */
  public static patchNamespacesGeofencerNamespacesNamespaceIdPatch(
    namespaceId: string,
    requestBody: NamespaceUpdate
  ): CancelablePromise<NamespaceResponse> {
    return __request(OpenAPI, {
      method: "PATCH",
      url: "/geofencer/namespaces/{namespace_id}",
      path: {
        namespace_id: namespaceId,
      },
      body: requestBody,
      mediaType: "application/json",
      errors: {
        404: `Namespace does not exist`,
        409: `Namespace exists`,
        422: `Validation Error`,
      },
    });
  }
}
