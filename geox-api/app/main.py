from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .model import GeoLiftParams

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"message": "OK"}


@app.post("/geolift/validate")
async def validate_params(params: GeoLiftParams):
    return {**params}
