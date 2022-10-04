/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CeleryTaskResponse } from "../models/CeleryTaskResponse";
import type { CeleryTaskResult } from "../models/CeleryTaskResult";

import type { CancelablePromise } from "../core/CancelablePromise";
import { OpenAPI } from "../core/OpenAPI";
import { request as __request } from "../core/request";

export class TasksService {
  /**
   * Get Status
   * Retrieve results of a task.
   * @param taskId
   * @returns CeleryTaskResult Successful Response
   * @throws ApiError
   */
  public static getStatusTasksResultsTaskIdGet(
    taskId: string
  ): CancelablePromise<CeleryTaskResult> {
    return __request(OpenAPI, {
      method: "GET",
      url: "/tasks/results/{task_id}",
      path: {
        task_id: taskId,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }

  /**
   * Run Test Celery
   * Run a test celery task.
   * @param word
   * @returns CeleryTaskResponse Successful Response
   * @throws ApiError
   */
  public static runTestCeleryTasksTestPost(
    word: string = "Hello"
  ): CancelablePromise<CeleryTaskResponse> {
    return __request(OpenAPI, {
      method: "POST",
      url: "/tasks/test",
      query: {
        word: word,
      },
      errors: {
        422: `Validation Error`,
      },
    });
  }
}
