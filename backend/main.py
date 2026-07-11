from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.api.routes import router as api_router
from app.api.phishing import router as phishing_router
from app.api.health import router as health_router
from app.api.cctv import router as cctv_router

app = FastAPI(
    title="Undersec Security Gateway",
    description="ML-powered database anomaly detection",
    version="1.0.0"
)

import os

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,chrome-extension://*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# THIS IS THE CRITICAL LINE:
app.include_router(api_router, prefix="/api")
app.include_router(phishing_router, prefix="/api/phishing")
app.include_router(health_router, prefix="/api/health")
app.include_router(cctv_router, prefix="/api/cctv")

@app.get("/")
def read_root():
    return {"status": "Undersec Gateway is running smoothly."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}