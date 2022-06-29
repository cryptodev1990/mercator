import os

import pandas as pd
from celery import Celery
from pandas import DataFrame
from app.model import MarketSelectionInput, MarketSelectionResult

from pygeolift.geolift import geo_data_read, geo_lift_market_selection

REDIS_CONNECTION = os.getenv("REDIS_CONNECTION", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks", broker=REDIS_CONNECTION, backend=REDIS_CONNECTION
)

@celery_app.task
def run_market_selection(input: MarketSelectionInput) -> MarketSelectionResult:
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
