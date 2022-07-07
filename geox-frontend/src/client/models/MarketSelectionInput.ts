/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { MarketSelectionInputDataRow } from './MarketSelectionInputDataRow';
import type { TestSidedness } from './TestSidedness';

/**
 * Input parameters for the market selection input call.
 */
export type MarketSelectionInput = {
    /**
     * Data
     */
    data: Array<MarketSelectionInputDataRow>;
    /**
     * Cost per incremental conversion.
     */
    cpic?: number;
    /**
     * Maximum budget that an experiment can spend.
     */
    budget?: number;
    /**
     * List of locations that must be included in treatment.
     */
    include_locations?: Array<string>;
    /**
     * List of locations that are not included in treatment.
     */
    exclude_locations?: Array<string>;
    /**
     * List of the number of experiment lengths (in days) to simulation.
     */
    treatment_periods?: Array<number>;
    /**
     * List of number of test markets to calculate power for.
     */
    num_locations?: Array<number>;
    /**
     * Effect sizes for which to calculate simulations. These must all be in the same direction.
     */
    effect_sizes?: Array<number>;
    /**
     * Number of simulations for each configuration to run.
     */
    num_simulations?: number;
    side_of_test?: TestSidedness;
    /**
     * Statistical significance value.
     */
    alpha?: number;
};

