// import { ApiResult } from "../core/ApiResult";
// import { ApiError } from "../core/ApiError";
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Result of a Celery task.
 */
export type CeleryTaskResult = {
  /**
   * Task id.
   */
  task_id: string;
  /**
   * Task status.
   */
  task_status: string;
  /**
   * Task results.
   */
  //   task_result: ApiResult | ApiError;
  task_result: any;
};
