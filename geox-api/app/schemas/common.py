import pydantic

# This is imported by __init__ with *
# Append all objects to exported in __all__
__all__ = ["BaseModel", "RequestErrorModel"]


class BaseModel(pydantic.BaseModel):
    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class RequestErrorModel(BaseModel):
    detail: str
