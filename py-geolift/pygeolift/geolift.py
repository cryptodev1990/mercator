"""Python package wrapper for R GeoLift package."""
import warnings
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Callable, Dict, List, Optional, Type, Union, Sequence

import numpy as np
import pandas as pd
import pandera as pa
from pandera import Column, DataFrameSchema
from pandera.typing import DataFrame, Series
from rpy2 import robjects
from rpy2.rinterface import ListSexpVector
from rpy2.robjects import ListVector, default_converter, pandas2ri
from rpy2.robjects.conversion import (Converter, NameClassMap, localconverter,
                                      rpy2py)
from rpy2.robjects.packages import importr


from .augsynth import AugSynth, AugSynthSummary, augsynth_converter
from .rpy2_utils import r_df_to_pandas, vector_to_py_scalar, check_rclass

__all__ = ["GEO_LIFT_TARGET_VERSION", "geo_lift", "GeoLiftDataFrameSchema"]

geo_lift = importr("GeoLift", on_conflict="warn")
"""Geo Lift R package"""


GEO_LIFT_TARGET_VERSION = "2.4"
if (geo_lift.__version__ is None) or (
    not geo_lift.__version__.startswith(GEO_LIFT_TARGET_VERSION)
):
    warnings.warn(
        f"This was designed againt GeoLift versions starting with {GEO_LIFT_TARGET_VERSION}"
        f" but you have {geo_lift.__version__}"
    )


class GeoLiftDataFrameSchema(pa.SchemaModel):
    """GeoLift data frame schema.

    This is the schema of a data frame after processed by `geo_data_read`.
    """

    location: Series[str] = pa.Field()
    time: Series[int] = pa.Field()
    Y: Series[float] = pa.Field()
    date_unix: Optional[Series[float]] = pa.Field()

    class Config:
        """Configuration."""

        strict = False


def geo_data_read(
    data: pd.DataFrame,
    date_id: str = "date",
    location_id: str = "location",
    Y_id: str = "units",
    format: str = "mm/dd/yyy",
    X: List[str] = [],
    summary: bool = False,
    keep_unix_time: bool = False,
) -> DataFrame[GeoLiftDataFrameSchema]:
    """Process and clean a data-frame for `geo_lift`."""
    with localconverter(default_converter + pandas2ri.converter):
        df = geo_lift.GeoDataRead(
            data,
            date_id=date_id,
            location_id=location_id,
            Y_id=Y_id,
            format=format,
            X=X,
            summary=summary,
            keep_unix_time=keep_unix_time,
        )
    return df


class RGeoLiftMarketSelection(robjects.ListVector):
    """Python wrapper for R `GeoLift::GeoLiftMarketSelection` objects."""

    _constructor = ["GeoLiftMarketSelection"]
    _rprint = ["print.GeoLiftMarketSelection"]

    @cached_property
    def BestMarkets(self) -> pd.DataFrame:
        with localconverter(robjects.default_converter + pandas2ri.converter):
            return robjects.conversion.py2rpy(self.rx2("BestMarkets"))

    @cached_property
    def PowerCurve(self) -> pd.DataFrame:
        with localconverter(robjects.default_converter + pandas2ri.converter):
            return robjects.conversion.py2rpy(self.rx2("PowerCurve"))

    @cached_property
    def parameters(self) -> pd.DataFrame:
        converters: Dict[str, Callable] = {
            "data": r_df_to_pandas,
            "model": vector_to_py_scalar,
            "cpic": vector_to_py_scalar,
            "side_of_test": vector_to_py_scalar,
            "fixed_effects": vector_to_py_scalar,
        }
        params = self.rx2("parameters")
        new_params = {}
        for name, func in converters.items():
            val = params.rx2(name)
            new_params[name] = func(val)
        return new_params



@dataclass
class GeoLiftMarketSelectionParameters:
    """Parameters used to run `geo_lift_market_selection`."""

    data: pd.DataFrame
    model: str
    cpic: float
    side_of_test: str
    fixed_effects: bool

    @classmethod
    def rpy2py(cls, obj: ListVector):
        """Convert to a python object."""
        cls(
            data = r_df_to_pandas(obj.rx2('data')),
            model = vector_to_py_scalar(obj.rx2("model")),
            cpic =vector_to_py_scalar(obj.rx2("cpic")),
            side_of_test = vector_to_py_scalar(obj.rx2("side_of_test")),
            fixed_effects = vector_to_py_scalar(obj.rx2["fixed_effects"])
        )

@dataclass
class GeoLiftMarketSelection:
    """Results of `geo_lift_market_selection`."""

    BestMarkets: pd.DataFrame
    PowerCurve: pd.DataFrame
    Parameters: GeoLiftMarketSelectionParameters

    @classmethod
    def rpy2py(cls, obj: ListVector):
        """Create from an object."""
        check_rclass(obj, 'GeoLiftMarketSelection')
        return cls(
            BestMarkets = r_df_to_pandas(obj.rx2("BestMarkets")),
            PowerCurve = r_df_to_pandas(obj.rx2("PowerCurve")),
            Parameters = GeoLiftMarketSelectionParameters.rpy2py(obj.rx2("parameters"))
        )

def geo_lift(
    data: pd.DataFrame,
    locations: Sequence[str],
    treatment_start_time: int,
    treatment_end_time: int,
    Y: str = "Y",
    X: Sequence[str] = (),
    alpha: float = 0.1,
    model: str = "none",
    fixed_effects: bool = True,
    ConfidenceIntervals: bool = False,
    stat_test: str = "Total"
):
    """Runs the R function `GeoLift::GeoLift`."""
    with localconverter(robjects.default_converter + pandas2ri.converter):
        return rpy2py(self.rx2("PowerCurve"))


class RGeoLift(robjects.ListVector):
    """Python wrapper for R GeoLift::GeoLift objects."""

    _constructor = ["GeoLift"]
    _rprint = ["print.GeoLift"]

    @cached_property
    def results(self) -> AugSynth:
        with localconverter(robjects.default_converter + augsynth_converter):
            return rpy2py(self.rx2("results"))

    @cached_property
    def inference(self) -> pd.DataFrame:
        return r_df_to_pandas(self.rx2("inference"))

    @cached_property
    def y_obs(self) -> np.array:
        return np.asarray(self.rx2("y_obs"))

    @cached_property
    def y_hat(self) -> np.array:
        return np.asarray(self.rx2("y_hat"))

    @cached_property
    def ATT(self) -> np.array:
        return np.asarray(self.rx2("ATT"))

    @cached_property
    def ATT_se(self):
        return self.rx2("ATT_se")

    @cached_property
    def TreatmentStart(self) -> int:
        return vector_to_py_scalar(self.rx2("TreatmentStart"))

    @cached_property
    def TreatmentEnd(self) -> int:
        return vector_to_py_scalar(self.rx2("TreatmentEnd"))

    @cached_property
    def test_id(self):
        return r_df_to_pandas(self.rx2("test_id"))

    @cached_property
    def incremental(self) -> float:
        return vector_to_py_scalar(self.rx2("incremental"))

    @cached_property
    def Y_id(self) -> str:
        return vector_to_py_scalar(self.rx2("Y_id"))

    @cached_property
    def summary(self) -> AugSynthSummary:
        with localconverter(robjects.default_converter + augsynth_converter):
            return rpy2py(self.rx2("summary"))

    @cached_property
    def ConfidenceIntervals(self) -> Optional[bool]:
        return bool(vector_to_py_scalar(self.rx2("ConfidenceInterval")))

    @cached_property
    def lower_bound(self) -> Optional[float]:
        return float(vector_to_py_scalar(self.rx2("lower_bound")))

    @cached_property
    def upper_bound(self) -> Optional[float]:
        return vector_to_py_scalar(self.rx2("lower_bound"))

    @cached_property
    def df_weights(self) -> pd.DataFrame:
        return r_df_to_pandas(self.rx2("df_weights"))

    @cached_property
    def stat_test(self) -> Optional[str]:
        return vector_to_py_scalar(self.rx2("lower_bound"))


@dataclass
class GeoLift:
    """Results of `geo_lift`."""

    results: AugSynth
    inference: pd.DataFrame
    y_obs: np.array
    y_hat: np.array
    ATT: np.array
    ATT_se: np.array
    TreatmentStart: int
    TreatmentEnd: int
    test_id: pd.DataFrame
    incremental: float
    Y_id: str
    summary: AugSynthSummary
    ConfidenceIntervals: Optional[bool]
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    df_weights: pd.DataFrame
    stat_test: Optional[str]

    @classmethod
    def rpy2py(cls: Type["GeoLift"], obj: ListVector) -> "GeoLift":
        """Convert from an R object."""
        check_rclass(obj, "AugSynth")
        data = {}
        data["y_obs"] = np.as_array(obj.rx2("y_obs"))
        data["y_hat"] = np.as_array(obj.rx2("y_hat"))
        data["ATT"] = np.as_array(obj.rx2("ATT"))
        data["ATT_se"] = np.as_array(obj.rx2("ATT_se"))
        data["TreatmentStart"] = vector_to_py_scalar(obj.rx2("TreatmentStart"))
        data["TreatmentEnd"] = vector_to_py_scalar(obj.rx2("TreatmentEnd"))
        data["test_id"] = r_df_to_pandas(obj.rx2("test_id"))
        data["incremental"] = vector_to_py_scalar(obj.rx2("incremental"))
        data["Y_id"] = vector_to_py_scalar(obj.rx2("Y_id"))
        with localconverter(robjects.default_converter + augsynth_converter):
            data["results"] = rpy2py(obj.rx2("results"))
            data["summary"] = rpy2py(obj.rx2("summary"))
        data["ConfidenceIntervals"] = vector_to_py_scalar(obj.rx2("ConfidenceInterval"))
        data["lower_bound"] = vector_to_py_scalar(obj.rx2("lower_bound"))
        data["upper_bound"] = vector_to_py_scalar(obj.rx2("lower_bound"))
        data["df_weights"] = r_df_to_pandas(obj.rx2("df_weights"))
        data["stat_test"] = vector_to_py_scalar(obj.rx2("lower_bound"))
        return cls(**data)

geo_lift_converter = Converter("GeoLiftConverter")
"""rpy2 converter for GeoLift package objects."""

geo_lift_converter.rpy2py_nc_map[ListSexpVector] = NameClassMap(
    ListSexpVector,
    {"GeoLiftMarketSelection": GeoLiftMarketSelection, "GeoLift": GeoLift},
)
geo_lift_converter += augsynth_converter
