import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from schemas import HealthResponse
from model import classifier
from routers import classify

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(classify.router, tags=["classification"])


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health():
    return {"status": "ok", "classes": list(classifier.names.values())}


@app.get("/", tags=["health"])
def root():
    return {"message": settings.app_name, "docs": "/docs"}