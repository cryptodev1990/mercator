/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CeleryAddTaskResult } from '../models/CeleryAddTaskResult';
import type { CeleryTaskRunResponse } from '../models/CeleryTaskRunResponse';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class TasksService {

    /**
     * Run Add Task
     * @param a
     * @param b
     * @returns CeleryTaskRunResponse Successful Response
     * @throws ApiError
     */
    public static runAddTaskTasksAddPost(
        a: number,
        b: number,
    ): CancelablePromise<CeleryTaskRunResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tasks/add',
            query: {
                'a': a,
                'b': b,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Get Status
     * @param taskId
     * @returns CeleryAddTaskResult Successful Response
     * @throws ApiError
     */
    public static getStatusTasksTaskIdGet(
        taskId: string,
    ): CancelablePromise<CeleryAddTaskResult> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks/{task_id}',
            path: {
                'task_id': taskId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
