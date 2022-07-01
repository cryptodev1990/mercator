import os
from typing import List, Optional

import pandas as pd
from celery import Celery
from pandas import DataFrame
from pydantic import BaseModel, Field
from pygeolift.geolift import geo_data_read, geo_lift_market_selection

from app.model import MarketSelectionInput

REDIS_CONNECTION = os.getenv("REDIS_CONNECTION", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks", broker=REDIS_CONNECTION, backend=REDIS_CONNECTION
)


class PowerCurveValue(BaseModel):
    """Power curve value in the market selection API results."""

    location: str = Field(..., description="Location id")
    duration: int = Field(..., description="Length of experiment assignment (in days)")
    Effect_size: float = Field(
        ...,
        description="Effect size used in the simulation. The treatmente values in the simulation are `(1 + EffectSize) * Y`.",
    )
    power: float = Field(..., description="Power (proportion of stat sig simulations)")
    Investment: float = Field(..., description="Investment, equal to `CPIC * Y`)")
    AvgATT: float = Field(
        ..., description="Average treatment effect for the treated units."
    )
    AvgDetectedLift: float = Field(..., description="Average detected lift.")


class LocationAssignment(BaseModel):

    location: List[str] = Field(..., description="Sorted list of location identifiers.")
    duration: int = Field(..., description="Length of experiment assignment (in days).")
    EffectSize: float = Field(
        ...,
        description="Smallest effect size for that (location combination, duration) where power is at least 80%.",
    )
    Power: float = Field(..., description="Power at the smallest effect size.")
    AvgScaledL2Imbalance: float = Field(..., description="Average scaled L2 imbalance.")
    Investment: float = Field(..., description="Estimated marketing budget for this.")
    AvgATT: float = Field(..., description="Average ATT estimate in simulations.")
    Average_MDE: float = Field(..., description="Average MDE in simulations.")
    ProportionTotal_Y: float = Field(..., description="Proportion of total Y.")
    abs_lift_in_zero: float = Field(
        ...,
        description="Estimated lift when there is no treatment effect. This should be close to 0.",
    )
    Holdout: float = Field(...)
    rank: int = Field(
        ...,
        description="Ranking of best designs. This the average rank of the ranks of (TODO).",
    )
    correlation: Optional[float] = Field(None)
    power_curve: List[PowerCurveValue] = Field(
        ...,
        description="A data frame with the results for all effect sizes that were estimated",
    )

class MarketSelectionResult(BaseModel):
    __root__: List[LocationAssignment] = Field(
        ..., description="List of assignments and information about those assignments."
    )


@celery_app.task
def run_market_selection_task(input: MarketSelectionInput):
    """Select locations for a geo-lift experiment."""
    df = pd.DataFrame.from_records([row.dict() for row in input.data])
    df["date"] = [d.strftime("%Y-%m-%d") for d in df["date"]]
    # TODO: add checks and cleaning functions in Python to replace this function
    data_clean = geo_data_read(
        df,
        date_id="date",
        Y_id="Y",
        location_id="location",
        format="yyyy-mm-dd",
        keep_unix_time=True,
        summary=False,
    )

    # Run main function
    results = geo_lift_market_selection(
        data=data_clean,
        treatment_periods=input.treatment_periods,
        N=input.num_locations,
        # X = tuple(),
        effect_size=input.effect_sizes,
        lookback_window=input.num_simulations,
        Y_id="Y",
        location_id="location",
        time_id="time",
        include_markets=input.include_locations,
        exclude_markets=input.exclude_locations,
        cpic=input.cpic,
        budget=input.budget,
        alpha=input.alpha,
        fixed_effects=True,
        normalize=False,
        side_of_test=str(input.side_of_test),
        # These should be set internally
        Correlations=True,
        parallel=False,
        parallel_setup="sequential",
        ProgressBar=False,
        print_=False,
    )

    # results.PowerCurves['duration'] = results.PowerCurves['duration'].astype(int)
    power_curves = dict(list(results.PowerCurves.groupby(["location", "duration"])))
    output = []
    # Post process results
    for row in results.BestMarkets.sort_values(["rank"]).itertuples(index=False):
        d = row._asdict()
        d["power_curve"] = power_curves[(row.location, row.duration)].to_dict(
            orient="records"
        )
        d["location"] = d["location"].split(",")
        d["duration"] = int(d["duration"])
        output.append(d)
    # TODO: Should the original parameters be included in the results
    return MarketSelectionResult(__root__=output)
