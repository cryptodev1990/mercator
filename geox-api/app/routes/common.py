from typing import Union

from fastapi import Header

HeaderType = Union[str, None]
header_default = Header(default=None)
