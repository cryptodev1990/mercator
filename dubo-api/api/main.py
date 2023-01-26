from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.handlers.api import router as api_router

app = FastAPI()
app.router.include_router(api_router, prefix="/v1")

@app.get("/")
def read_root():
    return "Have no sphere - Copyright Mercator 2023"


# Regex that matches a SQL table schema
# Allow quoted table names and column names
SQL_TABLE_REGEX = r"""
    ^CREATE\s+TABLE.*\(
"""

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)