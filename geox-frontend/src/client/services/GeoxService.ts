/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CeleryTaskRunResponse } from '../models/CeleryTaskRunResponse';
import type { MarketSelectionInput } from '../models/MarketSelectionInput';
import type { MarketSelectionTaskResult } from '../models/MarketSelectionTaskResult';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class GeoxService {

    /**
     * Run Market Selection
     * Submit a market selection task.
     * @param requestBody
     * @returns CeleryTaskRunResponse Successful Response
     * @throws ApiError
     */
    public static runMarketSelectionTasksMarketSelectionPost(
        requestBody: MarketSelectionInput,
    ): CancelablePromise<CeleryTaskRunResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tasks/market_selection',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Status
     * Retrieve results of a market selection task.
     * @param taskId
     * @returns MarketSelectionTaskResult Successful Response
     * @throws ApiError
     */
    public static getStatusTasksMarketSelectionTaskIdGet(
        taskId: string,
    ): CancelablePromise<MarketSelectionTaskResult> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks/market_selection/{task_id}',
            path: {
                'task_id': taskId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
