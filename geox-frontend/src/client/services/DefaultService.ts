/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AppVersion } from '../models/AppVersion';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DefaultService {

    /**
     * Info
     * Return app info.
     * @returns AppVersion Successful Response
     * @throws ApiError
     */
    public static infoInfoGet(): CancelablePromise<AppVersion> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/info',
        });
    }

    /**
     * Current User
     * @returns any Successful Response
     * @throws ApiError
     */
    public static currentUserCurrentUserGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/current_user',
        });
    }

    /**
     * Home
     * @returns any Successful Response
     * @throws ApiError
     */
    public static homeGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }

}
