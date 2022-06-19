"""Utility functions and classes to make working with rpy2 easier."""
from functools import singledispatch
from typing import Callable, Dict, Optional, Tuple

import pandas as pd
import rpy2.rinterface_lib.callbacks
from rpy2 import robjects
from rpy2.robjects import NA_Character, NA_Integer, NA_Logical, pandas2ri
from rpy2.robjects.conversion import localconverter
from rpy2.robjects.packages import importr
from rpy2.robjects.robject import RObjectMixin
from rpy2.robjects.vectors import BoolVector, FloatVector, IntVector, StrVector
import rpy2.robjects.vectors

__all__ = ["r_df_to_pandas", "vector_to_py_scalar"]

base = importr("base")


def r_df_to_pandas(df: rpy2.robjects.vectors.DataFrame) -> pd.DataFrame:
    """Convert an R dataframe to pandas."""
    with localconverter(robjects.default_converter + pandas2ri.converter):
        return robjects.conversion.rpy2py(df)

def pandas_to_r_df(df: pd.DataFrame) -> rpy2.robjects.vectors.DataFrame:
    """Convert an R dataframe to pandas."""
    with localconverter(robjects.default_converter + pandas2ri.converter):
        return robjects.conversion.py2rpy(df)

@singledispatch
def vector_to_py_scalar(x):
    """Convert homogeneous R vectors with 0 or 1 elements to python scalars."""
    return NotImplemented


def _vector_to_scalar(func):
    def wrapper(x):
        if len(x) == 0:
            return None
        if len(x) > 1:
            raise ValueError("Vector must have a length of 1.")
        return func(x[0])

    return wrapper


@vector_to_py_scalar.register(BoolVector)
@_vector_to_scalar
def vector_to_py_scalar_bool(x) -> Optional[bool]:
    return bool(x) if x != NA_Logical else None


@vector_to_py_scalar.register(IntVector)
@_vector_to_scalar
def vector_to_py_scalar_int(x) -> Optional[int]:
    return int(x) if x != NA_Integer else None


@vector_to_py_scalar.register(FloatVector)
@_vector_to_scalar
def vector_to_py_scalar_float(x) -> Optional[float]:
    # use is.finite() to convert NaN, Inf, and NA_Real to None
    return float(x) if bool(base.is_finite(x)[0]) else None



@vector_to_py_scalar.register(StrVector)
@_vector_to_scalar
def vector_to_py_scalar_str(x) -> Optional[str]:
    return str(x) if x != NA_Character else None


class RClassValueException(Exception):
    """R object does not have the specified S3 class."""

    pass


def check_rclass(obj: RObjectMixin, cls: str) -> None:
    """Check whether an R object has an S3 class.

    Raises:
        A `RClassValueException` if `obj` does not have
        `cls` in its R `class` attributed.
    """
    if cls not in list(obj.rclass):
        raise RClassValueException


class RCallbackContext:
    """Context manager for setting R callbacks.

    See https://rpy2.github.io/doc/v3.5.x/html/callbacks.html#console-i-o

    Attributes:
        consoleread: Function to use for :py:func:`rpy2.rinterface_lib.callbacks.consoleread`
        consolewrite_print:
        consolewrite_warnerror:
        showmessage:
        consoleflush:
        yesnocancel:
        showfiles:
        processevents:
        busy:
        cleanup:
    """

    _callbacks = [
        "consoleread",
        "consolewrite_print",
        "consolewrite_warnerror",
        "showmessage",
        "consoleflush",
        "yesnocancel",
        "showfiles",
        "processevents",
        "busy",
        "cleanup",
    ]

    def __init__(
        self,
        consoleread: Optional[Callable[[str], str]] = None,
        consolewrite_print: Optional[Callable[[str], None]] = None,
        consolewrite_warnerror: Optional[Callable[[str], None]] = None,
        showmessage: Optional[Callable[[str], None]] = None,
        consoleflush: Optional[Callable[[], None]] = None,
        yesnocancel: Optional[Callable[[str], None]] = None,
        showfiles: Optional[
            Callable[
                [Tuple[str, ...], Tuple[str, ...], Optional[str], Optional[str]], None
            ]
        ] = None,
        processevents: Optional[Callable[[], None]] = None,
        busy: Optional[Callable[[int], None]] = None,
        cleanup: Optional[Callable[..., Optional[int]]] = None,
    ):
        self._callback_cache: Dict[str, Callable] = {}
        # TODO: check validity of these
        self.consoleread = consoleread
        self.consolewrite_print = consolewrite_print
        self.consolewrite_warnerror = consolewrite_warnerror
        self.showmessage = showmessage
        self.consoleflush = consoleflush
        self.yesnocancel = yesnocancel
        self.showfiles = showfiles
        self.processevents = processevents
        self.busy = busy
        self.cleanup = cleanup

    def __enter__(self):
        # Cache current values of callbacks
        for cb in self._callbacks:
            self._callback_cache[cb] = getattr(rpy2.rinterface_lib.callbacks, cb)
        # Set any new callbacks
        for cb in self._callbacks:
            setattr(rpy2.rinterface_lib.callbacks, cb, getattr(self, cb))
        return self

    def __exit__(self, *excdetails) -> None:
        # Cache current values of callbacks
        for cb in self._callbacks:
            setattr(rpy2.rinterface_lib.callbacks, cb, self._callback_cache[cb])


def _console_donothing(s: str) -> None:
    pass


def suppress_output(print=True, warnerror=False) -> RCallbackContext:
    """Create a context to suppress R output.

    Args:
        print: Suppress standard output
        warnerror: Suppress warnings and errors
    Returns:
        An object of `RCallbackContext` to use with a ``with`` statement to
        suppress R output.

    """
    callbacks: Dict[str, Callable] = {}
    if print:
        callbacks["consolewrite_print"] = _console_donothing
    if warnerror:
        callbacks["consolewrite_warnerror"] = _console_donothing
    return RCallbackContext(**callbacks)
