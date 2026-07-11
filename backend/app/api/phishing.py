from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import time
from app.ml.phishing_model import predict_phishing_risk
from app.genai.explainer import generate_explanation

router = APIRouter()

class PhishingRequest(BaseModel):
    url: str

@router.post("/analyze")
async def analyze_phishing(req: PhishingRequest):
    start = time.time()
    
    result = await run_in_threadpool(predict_phishing_risk, req.url)
    
    ai_explanation = None
    if result["status"] in ["FLAGGED", "BLOCKED"]:
        ai_explanation = await run_in_threadpool(
            generate_explanation,
            query=f"[URL ANALYSIS] {req.url}",
            score=result["score"] / 100.0,
            user="system",
            features=result["features"]
        )
    else:
        ai_explanation = "URL looks safe based on structural analysis."
        
    execution_time = round((time.time() - start) * 1000, 2)
    
    return {
        "url": req.url,
        "score": result["score"],
        "level": result["level"],
        "status": result["status"],
        "reasons": result["reasons"],
        "explanation": ai_explanation,
        "execution_time_ms": execution_time
    }
