from app.genai.explainer import generate_explanation
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time
import random # Added for dynamic score fluctuating

from app.db.database import get_db
from app.db.models import QueryLog, Alert
from app.core.feature_extractor import extract_features, features_to_vector
from app.ml.predictor import predict_query_risk

router = APIRouter()

# --- DYNAMIC MEMORY STATE ---
SECURITY_SETTINGS = {
    "ml_block_threshold": -0.05,
    "medium_rule_score": -0.0450
}

# Pydantic schema for incoming requests
class QueryRequest(BaseModel):
    query: str
    user: str = "app_user"

@router.post("/query")
def process_query(req: QueryRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    q_upper = req.query.upper()
    
    # 1. ALWAYS Run ML Extraction & Prediction first
    # This ensures we always have a dynamic score for the UI
    estimated_rows = 10000 if any(kw in q_upper for kw in ["DROP", "DELETE", "TRUNCATE", "ALTER"]) else 1
    features = extract_features(req.query, req.user, time_of_day=14, rows_affected=estimated_rows)
    feature_vector = features_to_vector(features)
    
    # Get the raw ML result
    ml_result = predict_query_risk(feature_vector, SECURITY_SETTINGS["ml_block_threshold"])
    
    # --- DYNAMIC SCORE FUZZING ---
    # We add a tiny bit of random noise (-0.005 to +0.005) 
    # so the dashboard graph looks "alive" even for the same query.
    fuzzed_score = round(ml_result["score"] + random.uniform(-0.005, 0.005), 4)
    
    # --- THE HYBRID SECURITY GATEWAY (With Overrides) ---
    final_status = ml_result["status"]
    final_level = ml_result["level"]
    is_hardcoded = False

    # Rule 1: Hardcoded Veto for Destructive Commands
    if features.get("schema_change", 0) > 0 or any(kw in q_upper for kw in ["DROP", "TRUNCATE", "ALTER"]):
        final_status = "BLOCKED"
        final_level = "HIGH RISK"
        is_hardcoded = True
        
    # Rule 2: Hardcoded Veto for SQL Injection Signatures
    elif "UNION" in q_upper or "1=1" in q_upper or "--" in q_upper:
        final_status = "BLOCKED"
        final_level = "HIGH RISK"
        is_hardcoded = True

    # Rule 3: Hardcoded Flag for Suspicious Logic (Medium)
    elif q_upper.count(" OR ") >= 2 or q_upper.count("SELECT") > 1:
        if final_status != "BLOCKED": # Don't downgrade a Block to a Flag
            final_status = "FLAGGED"
            final_level = "MEDIUM RISK"
            is_hardcoded = True

    # -----------------------------------
    
    q_type = q_upper.split()[0] if q_upper else "UNKNOWN"
    execution_time = round((time.time() - start_time) * 1000, 2)
    
    # 2. Log to Database
    log_entry = QueryLog(
        query_text=req.query,
        db_user=req.user,
        query_type=q_type,
        anomaly_score=fuzzed_score, # Use the fuzzed score for the UI
        status=final_status,        # Use the hardcode-aware status
        execution_time=execution_time
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    # 3. Create Alert if Suspicious (ML or Hardcoded)
    if final_status in ["BLOCKED", "FLAGGED"]:
        # Generate the explanation using our GenAI layer
        ai_explanation = generate_explanation(
            query=req.query,
            score=fuzzed_score,
            user=req.user,
            features=features
        )
        
        # Tag the explanation if it was a hardcoded catch
        if is_hardcoded:
            ai_explanation = f"[Policy Override] {ai_explanation}"

        alert = Alert(
            query_id=log_entry.id,
            risk_level=final_level,
            explanation=ai_explanation
        )
        db.add(alert)
        db.commit()

    return {
        "id": log_entry.id,
        "status": final_status,
        "risk_level": final_level,
        "score": fuzzed_score,
        "execution_time_ms": execution_time,
        "hardcoded_catch": is_hardcoded
    }

@router.get("/activity")
def get_activity(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(limit).all()

@router.get("/alerts")
def get_alerts(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.created_at.desc()).limit(limit).all()

@router.get("/settings")
def get_settings():
    return SECURITY_SETTINGS

@router.put("/settings")
def update_settings(new_settings: dict):
    SECURITY_SETTINGS.update(new_settings)
    return SECURITY_SETTINGS