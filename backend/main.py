from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.api.routes import router as api_router

app = FastAPI(
    title="Undersec Security Gateway",
    description="ML-powered database anomaly detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

# THIS IS THE CRITICAL LINE:
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "Undersec Gateway is running smoothly."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}