"""Example datasets."""
import importlib.resources
import pandas as pd
from functools import lru_cache

__all__ = ["load_GeoLift_PreTest", "load_GeoLift_Test"]


def _get_csv(filename: str, **kwargs) -> pd.DataFrame:
    with importlib.resources.open_text('pygeolift.data', filename) as f:
        return pd.read_csv(f, **kwargs)

@lru_cache(1)
def load_GeoLift_PreTest() -> pd.DataFrame:
    """Load GeoLift example data `GeoLift_PreTest`."""
    return _get_csv("GeoLift_PreTest.csv")

@lru_cache(1)
def load_GeoLift_Test() -> pd.DataFrame:
    """Load GeoLift example data `GeoLift_Test`."""
    return _get_csv("GeoLift_Test.csv")
