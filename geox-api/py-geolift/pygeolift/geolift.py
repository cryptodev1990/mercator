"""Python package wrapper for R GeoLift package."""
import collections.abc
import warnings
from dataclasses import dataclass
from functools import cached_property, lru_cache
from locale import normalize
from typing import Callable, Dict, Optional, Sequence, Tuple, Type, Union, Any
from textwrap import dedent

import numpy as np
import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series
from rpy2 import robjects
from rpy2.rinterface import ListSexpVector
from rpy2.robjects import NULL as R_NULL
from rpy2.robjects import (
    FloatVector,
    IntVector,
    ListVector,
    StrVector,
    default_converter,
    pandas2ri,
)
from rpy2.robjects.conversion import Converter, NameClassMap, localconverter
from rpy2.robjects.packages import importr

from .augsynth import AugSynth, AugSynthSummary, augsynth_converter
from .rpy2_utils import check_rclass, r_df_to_pandas, vector_to_py_scalar

__all__ = [
    "GEO_LIFT_TARGET_VERSION",
    "geo_lift",
    "GeoLiftDataFrameSchema",
    "geo_lift_market_selection",
    "GeoLiftMarketSelection",
    "GeoLiftSummary",
]

rpackage = importr("GeoLift", on_conflict="warn")
"""Geo Lift R package"""


GEO_LIFT_TARGET_VERSION = "2.4"
if (rpackage.__version__ is None) or (
    not rpackage.__version__.startswith(GEO_LIFT_TARGET_VERSION)
):
    warnings.warn(
        f"This was designed againt GeoLift versions starting with {GEO_LIFT_TARGET_VERSION}"
        f" but you have {rpackage.__version__}"
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
    X: Sequence[str] = [],
    summary: bool = False,
    keep_unix_time: bool = False,
) -> DataFrame[GeoLiftDataFrameSchema]:
    """Process and clean a data-frame for `geo_lift`."""
    with localconverter(default_converter + pandas2ri.converter):
        df = rpackage.GeoDataRead(
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


@dataclass
class GeoLiftMarketSelectionParameters:
    """Parameters used to run `geo_lift_market_selection`."""

    data: pd.DataFrame
    model: str
    cpic: float
    side_of_test: str
    fixed_effects: bool

    @classmethod
    def rpy2py(
        cls: Type["GeoLiftMarketSelectionParameters"], obj: ListVector
    ) -> "GeoLiftMarketSelectionParameters":
        """Convert to a python object."""
        return cls(
            data=r_df_to_pandas(obj.rx2("data")),
            model=vector_to_py_scalar(obj.rx2("model")),
            cpic=vector_to_py_scalar(obj.rx2("cpic")),
            side_of_test=vector_to_py_scalar(obj.rx2("side_of_test")),
            fixed_effects=vector_to_py_scalar(obj.rx2("fixed_effects")),
        )


@dataclass
class GeoLiftMarketSelection:
    """Results of `geo_lift_market_selection`."""

    BestMarkets: pd.DataFrame
    PowerCurves: pd.DataFrame
    parameters: GeoLiftMarketSelectionParameters

    @classmethod
    def rpy2py(cls, obj: ListVector):
        """Create from an object."""
        check_rclass(obj, "GeoLiftMarketSelection")
        return cls(
            BestMarkets=r_df_to_pandas(obj.rx2("BestMarkets")),
            PowerCurves=r_df_to_pandas(obj.rx2("PowerCurves")),
            parameters=GeoLiftMarketSelectionParameters.rpy2py(obj.rx2("parameters")),
        )

    def __str__(self) -> str:
        """Print description of GeoLiftMarketSelection objects."""
        return str(self.BestMarkets)


def r_str_vector(obj: Union[str, Sequence[str]]) -> StrVector:
    if not isinstance(obj, str) and isinstance(obj, collections.abc.Sequence):
        return StrVector([str(elem) for elem in obj])
    return StrVector([str(obj)])


def geo_lift_market_selection(
    data: DataFrame[GeoLiftDataFrameSchema],
    treatment_periods: Sequence[int],
    N: Sequence[int] = tuple(),
    X: Sequence[str] = tuple(),
    Y_id: str = "Y",
    location_id: str = "location",
    time_id: str = "time",
    effect_size: Sequence[float] = list(np.arange(-0.2, 0.2, 0.05)),
    lookback_window: int = 1,
    include_markets: Sequence[str] = tuple(),
    exclude_markets: Sequence[str] = tuple(),
    holdout: Optional[Tuple[float, float]] = None,
    cpic: float = 1,
    budget: Optional[float] = None,
    alpha: float = 0.1,
    normalize: bool = False,
    model: str = "none",
    fixed_effects: bool = True,
    dtw: float = 0,
    Correlations: bool = False,
    ProgressBar: bool = False,
    print_: bool = True,
    run_stochastic_process: bool = False,
    parallel: bool = True,
    parallel_setup: str = "sequential",
    side_of_test: str = "two_sided",
    import_augsynth_from="library(augsynth)",
    import_tidyr_from="library(tidyr)",
):
    """Run the R function `GeoLift::GeoLift`."""
    with localconverter(default_converter + pandas2ri.converter):
        data_r = robjects.conversion.py2rpy(data)
    res = rpackage.GeoLiftMarketSelection(
        data_r,
        IntVector(treatment_periods),
        N=IntVector(N),
        X=r_str_vector(X),
        Y_id=str(Y_id),
        location_id=str(location_id),
        time_id=str(time_id),
        effect_size=FloatVector(effect_size),
        lookback_window=int(lookback_window),
        include_markets=r_str_vector(include_markets),
        exclude_markets=r_str_vector(exclude_markets),
        holdout=FloatVector(holdout[:2] if holdout is not None else []),
        cpic=float(cpic),
        budget=R_NULL if budget is None else float(budget),
        alpha=float(alpha),
        normalize=bool(normalize),
        model=str(model),
        fixed_effects=bool(fixed_effects),
        dtw=float(dtw),
        Correlations=bool(Correlations),
        ProgressBar=bool(ProgressBar),
        print=bool(print_),
        run_stochastic_process=bool(run_stochastic_process),
        parallel=bool(parallel),
        parallel_setup=str(parallel_setup),
        side_of_test=str(side_of_test),
        import_augsynth_from=str(import_augsynth_from),
        import_tidyr_from=str(import_tidyr_from),
    )
    return GeoLiftMarketSelection.rpy2py(res)


@dataclass
class GeoLiftInference:
    ATT: float
    Perc_Lift: float
    pvalue: float
    Lower_Conf_Int: Optional[float]
    Upper_Conf_Int: Optional[float]


@dataclass
class GeoLiftSummary:
    """Summary of a GeoLift experiment."""

    ATT_est: float
    PercLift: float
    pvalue: float
    LowerCI: Optional[float]
    UpperCI: Optional[float]
    L2Imbalance: float
    L2ImbalanceScaled: float
    ATT: float
    start: int
    end: int
    type: str
    Y_id: str
    incremental: float
    bias: Optional[float]
    weights: float
    CI: bool
    alpha: float
    lower: Optional[float]
    upper: Optional[float]
    factor: int
    progfunc: str


    def __str__(self) -> str:
        """Summarize object."""
        ci_alpha = (1 - self.alpha) * 100
        if self.lower is not None and self.upper is not None:
            ci_values = (self.lower * self.factor, self.upper * self.factor)
            CI_string = f"{ci_alpha}% Confidence Interval: ({ci_values[0]:.3f}, {ci_values[1]:.3f})"
        else:
            CI_string = f"{ci_alpha}% Confidence Interval: Not calculated"

        pct_improvement_balance = (1 - self.L2ImbalanceScaled) * 100
        bias = f"{self.bias:.3f}" if self.bias is not None else ""

        return dedent(f"""
        Statistics
        ----------
        Average ATT: {self.ATT_est:.3f}
        Percent Lift: {self.PercLift:.2f}%
        Incremental {self.Y_id}: {self.incremental:.2f}
        P-value: {self.pvalue:.2f}
        {CI_string}

        Balance
        -------
        L2 Imbalance: {self.L2Imbalance:.3f}
        Scaled L2 Imbalance: {self.L2ImbalanceScaled:.4f}
        Percent improvement from naive model: {pct_improvement_balance:.0f}%
        Average estimated bias: {bias}

        Model Weights
        -------------
        Prognostic function: {self.progfunc}

        """)


@dataclass
class GeoLift:
    """Results of `geo_lift`."""

    results: AugSynth
    inference: GeoLiftInference
    y_obs: np.ndarray
    y_hat: np.ndarray
    ATT: np.ndarray
    ATT_se: np.ndarray
    TreatmentStart: int
    TreatmentEnd: int
    test_id: pd.DataFrame
    incremental: float
    Y_id: str
    summary: AugSynthSummary
    ConfidenceIntervals: bool
    lower_bound: Optional[float]
    upper_bound: Optional[float]
    df_weights: pd.DataFrame
    stat_test: Optional[str]

    @classmethod
    def rpy2py(cls: Type["GeoLift"], obj: ListVector) -> "GeoLift":
        """Create object from an R object."""
        check_rclass(obj, "GeoLift")
        data: Dict[str, Any] = {}
        inference_df = r_df_to_pandas(obj.rx2("inference"))
        inference_df.columns = [c.replace(".", "_") for c in inference_df.columns]
        data["inference"] = GeoLiftInference(
            **next(inference_df.itertuples(index=False))._asdict()
        )
        data["y_obs"] = np.asarray(obj.rx2("y_obs"))
        data["y_hat"] = np.asarray(obj.rx2("y_hat"))
        data["ATT"] = np.asarray(obj.rx2("ATT"))
        data["ATT_se"] = np.asarray(obj.rx2("ATT_se"))
        data["TreatmentStart"] = vector_to_py_scalar(obj.rx2("TreatmentStart"))
        data["TreatmentEnd"] = vector_to_py_scalar(obj.rx2("TreatmentEnd"))
        data["test_id"] = r_df_to_pandas(obj.rx2("test_id"))
        data["incremental"] = vector_to_py_scalar(obj.rx2("incremental"))
        data["Y_id"] = vector_to_py_scalar(obj.rx2("Y_id"))
        data["results"] = AugSynth.rpy2py(obj.rx2("results"))
        data["summary"] = AugSynthSummary.rpy2py(obj.rx2("summary"))
        data["ConfidenceIntervals"] = vector_to_py_scalar(obj.rx2("ConfidenceInterval"))
        data["lower_bound"] = vector_to_py_scalar(obj.rx2("lower_bound"))
        data["upper_bound"] = vector_to_py_scalar(obj.rx2("lower_bound"))
        data["df_weights"] = r_df_to_pandas(obj.rx2("df_weights"))
        data["stat_test"] = vector_to_py_scalar(obj.rx2("lower_bound"))
        return cls(**data)

    @property
    def test_duration(self) -> int:
        """Test duration."""
        return self.TreatmentEnd - self.TreatmentStart + 1

    def __str__(self) -> str:
        test_markets = ", ".join(list(self.test_id["name"]))
        perc_lift = float(self.inference.Perc_Lift)
        att = float(self.inference.ATT)
        pvalue = self.inference.pvalue


        msg = dedent(
            f"""
        GeoLift Output

        Test Info
        ---------
        Test duration: {self.test_duration} periods
        Start time: {self.TreatmentStart}
        End time: {self.TreatmentEnd}
        Test markets: {test_markets}

        Statistics
        ----------
        PercentLift: {perc_lift:.3f}%
        Incremental {self.Y_id}: {self.incremental}
        ATT: {att:.2f}
        pvalue: {pvalue:.4f}

        """
        )
        return msg

    def summarize(self) -> GeoLiftSummary:
        """Return a summary of the GeoLift analysis."""
        return GeoLiftSummary(
            ATT_est=self.inference.ATT,
            PercLift=self.inference.Perc_Lift,
            pvalue=self.inference.pvalue,
            LowerCI=self.inference.Lower_Conf_Int,
            UpperCI=self.inference.Upper_Conf_Int,
            L2Imbalance=self.summary.l2_imbalance,
            L2ImbalanceScaled=self.summary.scaled_l2_imbalance,
            ATT=self.summary.att,
            start=self.TreatmentStart,
            end=self.TreatmentEnd,
            type="single",
            Y_id=self.Y_id,
            incremental=self.incremental,
            bias=float(np.mean(self.summary.bias_est)) if self.summary.bias_est is not None else None,
            weights=self.df_weights,
            CI=self.ConfidenceIntervals,
            alpha=self.summary.alpha,
            lower=self.lower_bound,
            upper=self.upper_bound,
            factor=int(self.results.data.y.shape[0] * self.test_id.shape[0]),
            progfunc=self.results.progfunc,
        )

def geo_lift(
    data: DataFrame[GeoLiftDataFrameSchema],
    locations: Union[str, Sequence[str]],
    treatment_start_time: int,
    treatment_end_time: int,
    Y_id: str = "Y",
    time_id: str = "time",
    location_id: str = "location",
    X: Sequence[str] = (),
    alpha: float = 0.1,
    model: str = "none",
    fixed_effects: bool = True,
    ConfidenceIntervals: bool = False,
    stat_test: str = "Total",
):
    """Run the R function `GeoLift::GeoLift`."""
    with localconverter(default_converter + pandas2ri.converter):
        data_r = robjects.conversion.py2rpy(data)
    res = rpackage.GeoLift(
        data=data_r,
        locations=r_str_vector(locations),
        treatment_start_time=int(treatment_start_time),
        treatment_end_time=int(treatment_end_time),
        Y_id=str(Y_id),
        time_id=str(time_id),
        location_id=str(location_id),
        X=r_str_vector(X),
        alpha=float(alpha),
        model=str(model),
        fixed_effects=bool(fixed_effects),
        ConfidenceIntervals=bool(ConfidenceIntervals),
        stat_test=str(stat_test)
    )
    # return res
    return GeoLift.rpy2py(res)


geo_lift_converter = Converter("GeoLiftConverter")
"""rpy2 converter for GeoLift package objects."""

geo_lift_converter.rpy2py_nc_map[ListSexpVector] = NameClassMap(
    ListSexpVector,
    {"GeoLiftMarketSelection": GeoLiftMarketSelection, "GeoLift": GeoLift},
)
geo_lift_converter += augsynth_converter
