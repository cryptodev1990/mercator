"""Words mapping to feature classes of OSM entities."""
import json
from importlib.resources import files
from typing import Dict

from pydantic.main import BaseModel  # pylint: disable=no-name-in-module


class FeatureClass(BaseModel):
    """Tag and value associated with an OSM feature class."""
    key: str
    value: str
    plural: bool


with files("app.data").joinpath("feature_classes.json").open("r", encoding="utf-8") as f:
    feature_classes: Dict[str, FeatureClass] = {
        k: FeatureClass.parse_obj(v) for k, v in json.load(f).items()
    }
