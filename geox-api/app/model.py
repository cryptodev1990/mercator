from pydantic import BaseModel

from typing import Any, Callable, Dict, Optional, Sequence, Tuple, Type, Union
from pandas import DataFrame

from pygeolift import geolift


class GeoLiftParams(BaseModel):

    data: Any
    locations: Sequence[str]
    treatment_start_time: int
    treatment_end_time: int
    Y_id: str = "Y"
    time_id: str = "time"
    location_id: str = "location"
    X: Sequence[str]
    alpha: float = 0.1
    model: str = "none"
    fixed_effects: bool = True
    ConfidenceIntervals: bool = False
    stat_test: str = "Total"
