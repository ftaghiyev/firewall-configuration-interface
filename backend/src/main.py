from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import policies
from .config import settings
import os

app = FastAPI(title="NL Firewall Configuration Interface", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,         
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Firewall Configuration Interface is running..."}


app.include_router(policies.router)