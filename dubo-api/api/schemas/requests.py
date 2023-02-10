from typing import List, Optional, Any
from pydantic import BaseModel


class DuboQuery(BaseModel):
    user_query: str
    schemas: List[str]
    descriptions: Optional[List[str]] = None
    data_header: Optional[List[str]] = None
    data_sample: Optional[List[List[Any]]] = None
