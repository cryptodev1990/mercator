/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PowerCurveValue } from './PowerCurveValue';

export type LocationAssignment = {
    /**
     * Sorted list of location identifiers.
     */
    location: Array<string>;
    /**
     * Length of experiment assignment (in days).
     */
    duration: number;
    /**
     * Smallest effect size for that (location combination, duration) where power is at least 80%.
     */
    EffectSize: number;
    /**
     * Power at the smallest effect size.
     */
    Power: number;
    /**
     * Average scaled L2 imbalance.
     */
    AvgScaledL2Imbalance: number;
    /**
     * Estimated marketing budget for this.
     */
    Investment: number;
    /**
     * Average ATT estimate in simulations.
     */
    AvgATT: number;
    /**
     * Average MDE in simulations.
     */
    Average_MDE: number;
    /**
     * Proportion of total Y.
     */
    ProportionTotal_Y: number;
    /**
     * Estimated lift when there is no treatment effect. This should be close to 0.
     */
    abs_lift_in_zero: number;
    Holdout: number;
    /**
     * Ranking of best designs. This the average rank of the ranks of (TODO).
     */
    rank: number;
    correlation?: number;
    /**
     * A data frame with the results for all effect sizes that were estimated
     */
    power_curve: Array<PowerCurveValue>;
};

