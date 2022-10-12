/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AppVersion } from "../models/AppVersion";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class DefaultService {
  /**
   * Info
   * Return app version information.
   * @returns AppVersion Successful Response
   * @throws ApiError
   */
  public static infoInfoGet(): CancelablePromise<AppVersion> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/info",
    });
  }

  /**
   * Home
   * @returns any Successful Response
   * @throws ApiError
   */
  public static homeGet(): CancelablePromise<any> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/",
    });
  }
}
