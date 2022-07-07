/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class HealthService {

    /**
     * Health
     * @returns any Successful Response
     * @throws ApiError
     */
    public static healthHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }

    /**
     * Protected Health
     * @returns any Successful Response
     * @throws ApiError
     */
    public static protectedHealthProtectedHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/protected_health',
        });
    }

    /**
     * Redis Health
     * @returns any Successful Response
     * @throws ApiError
     */
    public static redisHealthRedisHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/redis-health',
        });
    }

    /**
     * Db Health
     * @returns any Successful Response
     * @throws ApiError
     */
    public static dbHealthDbHealthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/db-health',
        });
    }

}
