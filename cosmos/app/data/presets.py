"""ID editor preset categories.

The object `presets` is a dictionary of Preset objects, keyed by the preset key.

"""
import json
from importlib.resources import files
from typing import Dict, List

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class Preset(BaseModel):
    """OSM Preset.

    In OSM world, general-purpose editors come with presets to make tagging features more user-friendl.
    Each preset automatically applies primary and secondary feature key or tag to a feature.

    These presets provide reasonable categories that incorporate OSM domain knowledge and an API that
    is already used by many OSM editors.

    The preset class here is the one used by the OSM ID editor.

    See

    - https://wiki.openstreetmap.org/wiki/Preset
    - https://github.com/ideditor/schema-builder/blob/main/schemas/preset.json for the JSON schema
    - https://github.com/openstreetmap/id-tagging-schema
    -

    """

    key: str
    name: str
    geometry: List[str] = Field(deffault_factory=list)
    tags: Dict[str, str] = Field(default_factory=dict)
    terms: List[str] = Field(default_factory=list)
    aliases: List[str] = Field(default_factory=list)
    searchable: bool = True

# TODO: the preset class could be automatically derived from its JSON schema definintion
# at https://github.com/ideditor/schema-builder/blob/main/schemas/preset.json
# However, I could not run `codegen <https://docs.pydantic.dev/datamodel_code_generator/>`__
# without an error.

with files("app.data").joinpath("presets.json").open("r", encoding="utf-8") as f:
    presets = {}
    k, v = None, None
    for k, v in json.load(f).items():
        v["key"] = k
        presets[k] = Preset.parse_obj(v)
    del k, v
