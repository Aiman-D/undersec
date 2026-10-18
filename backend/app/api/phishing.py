from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import time
from app.ml.phishing_model import predict_phishing_risk
from app.genai.explainer import generate_explanation

router = APIRouter()

# Memory buffer for recent phishing scans
RECENT_SCANS = []
MAX_SCANS = 50

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
            query=f"[URL HEURISTIC DPI] {req.url}",
            score=result["score"] / 100.0,
            user="chrome_extension",
            features=result["features"]
        )
    else:
        ai_explanation = "Domain structure conforms to legitimate web baselines across 7 heuristic parameters."
        
    execution_time = round((time.time() - start) * 1000, 2)
    
    entry = {
        "id": int(time.time() * 1000),
        "url": req.url,
        "score": result["score"],
        "level": result["level"],
        "status": result["status"],
        "reasons": result["reasons"],
        "features": result["features"],
        "explanation": ai_explanation,
        "execution_time_ms": execution_time,
        "timestamp": time.time()
    }
    
    RECENT_SCANS.insert(0, entry)
    if len(RECENT_SCANS) > MAX_SCANS:
        RECENT_SCANS.pop()
        
    return entry

@router.get("/recent")
async def get_recent_scans():
    """Returns the most recent URL scans and aggregated statistics."""
    total = len(RECENT_SCANS)
    blocked = sum(1 for s in RECENT_SCANS if s["status"] == "BLOCKED")
    flagged = sum(1 for s in RECENT_SCANS if s["status"] == "FLAGGED")
    safe = sum(1 for s in RECENT_SCANS if s["status"] == "ALLOWED")
    
    return {
        "total": total,
        "blocked": blocked,
        "flagged": flagged,
        "safe": safe,
        "scans": RECENT_SCANS[:25]
    }
