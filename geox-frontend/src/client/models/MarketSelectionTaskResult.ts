/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { MarketSelectionResult } from './MarketSelectionResult';

export type MarketSelectionTaskResult = {
    /**
     * Task id
     */
    task_id: any;
    /**
     * Task status.
     */
    task_status: string;
    /**
     * Market selection results.
     */
    task_result: MarketSelectionResult;
};

