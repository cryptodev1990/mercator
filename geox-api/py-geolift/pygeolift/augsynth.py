"""Python wrapper for the Augsynth R package."""
from dataclasses import dataclass
from typing import Any, Dict, Union, Optional, Type

import numpy as np
import pandas as pd
from rpy2.rinterface import ListSexpVector
from rpy2.robjects import ListVector
from rpy2.robjects.packages import importr
from rpy2.robjects.conversion import Converter, NameClassMap

from .rpy2_utils import r_df_to_pandas, vector_to_py_scalar, check_rclass

__all__ = ["augsynth", "AugSynth", "AugSynthSummary", "augsynth_converter"]

augsynth = importr("augsynth")
"""The augsynth R package."""

_base_r = importr("base")

@dataclass
class AugSynthData:
    """Stores data used in estimating an AugSynth model."""

    X: np.ndarray
    trt: np.ndarray
    y: np.ndarray
    time: np.ndarray
    synth_data: Dict[str, np.ndarray]

    @classmethod
    def rpy2py(cls: Type["AugSynthData"], obj: ListVector) -> "AugSynthData":
        """Convert from an R object to python."""
        data: Dict[str, Any] = {}
        for k in ("X", "trt", "y", "time"):
            data[k] = np.asarray(obj.rx2(k))
        data["synth_data"] = {}
        for k in ("Z0", "Z1", "Y0plot", "Y1plot", "X0", "X1"):
            data["synth_data"][k] = np.asarray(obj.rx2("synth_data").rx2(k))
        return cls(**data)


@dataclass
class AugSynth:
    """Store the results of an AugSynth model."""

    data: AugSynthData
    weights: np.ndarray
    l2_imbalance: float
    scaled_l2_imbalance: float
    mhat: np.ndarray
    lambda_: Optional[np.ndarray]
    ridge_mhat: np.ndarray
    synw: np.ndarray
    lambdas: Optional[np.ndarray]
    lambdas_errors: Optional[np.ndarray]
    lambdas_errors_se: Optional[np.ndarray]
    progfunc: str
    scm: bool
    fixedeff: bool
    t_int: int

    @classmethod
    def rpy2py(cls: Type["AugSynth"], obj: ListVector) -> "AugSynth":
        """Convert R object to Python class."""
        check_rclass(obj, "augsynth")
        args = {
            "weights": np.asarray(obj.rx2("weights")),
            "l2_imbalance": vector_to_py_scalar(obj.rx2("l2_imbalance")),
            "scaled_l2_imbalance": vector_to_py_scalar(obj.rx2("scaled_l2_imbalance")),
            "mhat": np.asarray(obj.rx2("mhat")),
            "lambda_": np.asarray(obj.rx2("lambda")),
            "ridge_mhat": np.asarray(obj.rx2("ridge_mhat")),
            "synw": np.asarray(obj.rx2("synw")),
            "lambdas": obj.rx2("lambdas"),
            "lambdas_errors": obj.rx2("lambdas_errors"),
            "lambdas_errors_se": obj.rx2("lambdas_errors_se"),
            "progfunc": vector_to_py_scalar(obj.rx2("progfunc")),
            "scm": vector_to_py_scalar(obj.rx2("scm")),
            "fixedeff": vector_to_py_scalar(obj.rx2("fixedeff")),
            "t_int": vector_to_py_scalar(obj.rx2("t_int")),
            "data": AugSynthData.rpy2py(obj.rx2("data")),
        }
        return cls(**args)


[
    "att",
    "average_att",
    "alpha",
    "t_int",
    "call",
    "l2_imbalance",
    "scaled_l2_imbalance",
    "bias_est",
    "inf_type",
]

>>>>>>> 625978e (Add lint)

@dataclass
class AugSynthSummary:
    """Python class for summary.augsynth."""

    att: pd.DataFrame
    average_att: pd.DataFrame
    alpha: float
    t_int: int
    l2_imbalance: float
    scaled_l2_imbalance: float
    bias_est: Optional[np.ndarray]
    inf_type: str

    @classmethod
    def rpy2py(cls: Type["AugSynthSummary"], obj: ListVector) -> "AugSynthSummary":
        """Convert R object to Python class."""
        check_rclass(obj, "summary.augsynth")
        bias_est_r = obj.rx2("bias_est")
        return cls(
            att=r_df_to_pandas(obj.rx2("att")),
            average_att=r_df_to_pandas(obj.rx2("average_att")),
            alpha=vector_to_py_scalar(obj.rx2("alpha")),
            t_int=vector_to_py_scalar(obj.rx2("t_int")),
            l2_imbalance=vector_to_py_scalar(obj.rx2("l2_imbalance")),
            scaled_l2_imbalance=vector_to_py_scalar(obj.rx2("scaled_l2_imbalance")),
            bias_est=None if bool(_base_r.all(_base_r.is_na(bias_est_r))) else np.asarray(bias_est_r),
            inf_type=vector_to_py_scalar(obj.rx2("inf_type")),
        )


augsynth_converter = Converter("augsynth conversions")
"""rpy2 converter for augsynth objects."""

augsynth_converter.rpy2py_nc_map[ListSexpVector] = NameClassMap(
    ListSexpVector,
    {"augsynth": AugSynth.rpy2py, "summary.augsynth": AugSynthSummary.rpy2py},
)
