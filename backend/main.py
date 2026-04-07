from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
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

@app.get("/")
def read_root():
    return {"status": "Undersec Gateway is running smoothly."}

@app.get("/health")
def health_check():
    return {"db_status": "pending", "ml_model_status": "pending"}