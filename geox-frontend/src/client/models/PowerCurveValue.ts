/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

/**
 * Power curve value in the market selection API results.
 */
export type PowerCurveValue = {
    /**
     * Location id
     */
    location: string;
    /**
     * Length of experiment assignment (in days)
     */
    duration: number;
    /**
     * Effect size used in the simulation. The treatmente values in the simulation are `(1 + EffectSize) * Y`.
     */
    Effect_size: number;
    /**
     * Power (proportion of stat sig simulations)
     */
    power: number;
    /**
     * Investment, equal to `CPIC * Y`)
     */
    Investment: number;
    /**
     * Average treatment effect for the treated units.
     */
    AvgATT: number;
    /**
     * Average detected lift.
     */
    AvgDetectedLift: number;
};

