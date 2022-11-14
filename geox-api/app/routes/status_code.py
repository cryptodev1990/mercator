"""Status code routes"""
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/status_code", tags=["status code"])
async def get_status_code(
    status_code: int = Query(..., description="The status code use for the response"),
):
    return JSONResponse(status_code=status_code, content={"status_code": status_code})
