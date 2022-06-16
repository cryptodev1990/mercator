import warnings

__VERSION__ = "0.0.1"

from rpy2 import robjects
from rpy2.robjects.packages import WeakPackage, importr

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    geo_lift_ = importr('GeoLift', on_conflict="warn")
    geo_lift = WeakPackage(geo_lift_._env,
                            geo_lift_.__rname__,
                            translation=geo_lift_._translation,
                            exported_names=geo_lift_._exported_names,
                            on_conflict="warn",
                            version=geo_lift_.__version__,
                            symbol_r2python=geo_lift_._symbol_r2python,
                            symbol_resolve=geo_lift_._symbol_resolve)

TARGET_VERSION = '2.4'
if (
  (geo_lift.__version__ is None)
  or
  (not geo_lift.__version__.startswith(TARGET_VERSION))
):
    warnings.warn(
        f"This was designed againt GeoLift versions starting with {TARGET_VERSION}"
        f" but you have {geo_lift.__version__}")

