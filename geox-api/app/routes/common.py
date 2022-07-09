from typing import Union

from fastapi import Header
from fastapi.security import HTTPBearer

security = HTTPBearer()

HeaderType = Union[str, None]
header_default = Header(default=None)
