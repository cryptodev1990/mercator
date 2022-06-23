import datetime
from enum import Enum
from typing import List, Optional, TypedDict

import pandas as pd
from pandas import DataFrame
from pydantic import (BaseModel, Field, PositiveFloat, PositiveInt, confloat,
                      root_validator, validator)
from pygeolift.geolift import geo_data_read, geo_lift_market_selection


class EnumStringPrint:
    def __str__(self):
        return str(self.value)


class TestSidedness(EnumStringPrint, str, Enum):
    one_sided = "one_sided"
    two_sided = "two_sided"


class MarketSelectionInputDataRow(BaseModel):
    location: str
    date: datetime.date
    Y: float


class PowerCurveValue(BaseModel):
    """Power curve value in the market selection API results."""

    location: str = Field(..., description="Location id")
    duration: int = Field(..., description="Length of experiment assignment (in days)")
    EffectSize: float = Field(
        ..., description="Effect size used in the simulation (relative)"
    )
    power: float = Field(..., description="Power (proportion of stat sig simulations)")
    Investment: float = Field(
        ..., description="Investment, equal to CPIC * conversions)"
    )
    AvgATT: float = Field(
        ..., description="Average treatment effect for the treated units"
    )
    AvgDetectedLift: float = Field(..., description="Average detected lift.")


class LocationAssignment(BaseModel):
    location: List[str] = Field(..., description="Sorted list of location identifiers")
    duration: int = Field(..., description="Length of experiment assignment (in days)")
    EffectSize: float = Field(
        ...,
        description="Smallest effect size for that (location combination, duration) where power is at least 80%.",
    )
    Power: float = Field(..., description="Power at the smallest effect size")
    AvgScaledL2Imbalance: float = Field(..., description="Average scaled L2 imbalance")
    Investment: float = Field(..., description="Estimated marketing budget for this")
    AvgATT: float = Field(..., description="Average ATT estimate in simulations")
    Average_MDE: float = Field(..., description="Average MDE in simulations")
    ProportionTotal_Y: float = Field(..., description="Proportion of total Y")
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

    class Config:
        arbitrary_types_allowed = True


class MarketSelectionResult(BaseModel):
    __root__: List[LocationAssignment] = Field(
        ..., description="List of assignments and information about those assignments."
    )


class MarketSelectionInput(BaseModel):
    data: List[MarketSelectionInputDataRow] = Field(..., description="Data ")
    treatment_periods: List[PositiveInt] = Field(
        ...,
        description="List of the number of experiment lengths (in days) to simulation.",
    )
    num_locations: List[PositiveInt] = Field(...)
    effect_sizes: List[float] = Field([0, 0.05, 0.10, 0.15, 0.20, 0.25])
    lookback_window: PositiveInt = Field(1)
    include_locations: List[str] = Field([])
    exclude_locations: List[str] = Field([])
    cpic: PositiveFloat = Field(1)
    budget: Optional[PositiveFloat] = Field(None)
    side_of_test: TestSidedness = Field(TestSidedness.one_sided)
    fixed_effects: bool = True
    alpha: confloat(gt=0, lt=1) = Field(
        0.05, description="Statistical significance value."
    )

    @validator("include_locations", "exclude_locations", "effect_sizes", pre=True)
    def uniquify_list(cls, v):
        """Ensure locations are always unique."""
        return list(set(v))

    # @validator('effect_sizes')
    # def check_effect_sizes(cls, v):
    #     # check that all effect sizes are in the same direction
    #     if sum(x >= 0 for x in v) != len(v):
    #         raise ValueError("Effect sizes must be either all positive or all negative.")
    #     return v

    @root_validator(pre=False)
    def check_include_locations(cls, values):
        include_locations = values.get("include_locations")
        if include_locations:
            locations = set(row.location for row in values.get("data"))
            missing_locations = set(include_locations) - locations
            if len(missing_locations) > 0:
                raise ValueError(
                    "Some locations in `include_locations` are not in `data`: {}".format(
                        ",".join(missing_locations)
                    )
                )
        return values

    @root_validator(pre=False)
    def check_exclude_locations(cls, values):
        exclude_locations = values.get("exclude_locations")
        if exclude_locations:
            locations = set(row.location for row in values.get("data"))
            missing_locations = set(exclude_locations) - locations
            if len(missing_locations) > 0:
                raise ValueError(
                    "Some locations in `exclude_locations` are not in `data`: {}".format(
                        ",".join(missing_locations)
                    )
                )
        return values


def market_selection(input: MarketSelectionInput) -> MarketSelectionResult:
    """Select locations for a geo-lift experiment."""
    df = pd.DataFrame.from_records([row.dict() for row in input.data])
    df["date"] = [d.strftime("%Y-%m-%d") for d in df["date"]]
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
        lookback_window=input.lookback_window,
        Y_id="Y",
        location_id="location",
        time_id="time",
        include_markets=input.include_locations,
        exclude_markets=input.exclude_locations,
        cpic=input.cpic,
        budget=input.budget,
        alpha=input.alpha,
        fixed_effects=input.fixed_effects,
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
