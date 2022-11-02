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
  task_result: any;
};