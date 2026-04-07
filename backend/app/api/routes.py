from app.genai.explainer import generate_explanation
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import time

from app.db.database import get_db
from app.db.models import QueryLog, Alert
from app.core.feature_extractor import extract_features, features_to_vector
from app.ml.predictor import predict_query_risk

router = APIRouter()

# Pydantic schema for incoming requests
class QueryRequest(BaseModel):
    query: str
    user: str = "app_user"

@router.post("/query")
def process_query(req: QueryRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    
    # Heuristic: If it's a destructive query, assume it affects massive amounts of rows
    q_upper = req.query.upper()
    estimated_rows = 10000 if any(kw in q_upper for kw in ["DROP", "DELETE", "TRUNCATE", "ALTER"]) else 1
    
    # 1. Extract ML Features
    features = extract_features(req.query, req.user, time_of_day=14, rows_affected=estimated_rows)
    feature_vector = features_to_vector(features)
    
    # --- THE HYBRID SECURITY GATEWAY ---
    # Rule 1: Instant Veto for Destructive Commands (DROP, ALTER, TRUNCATE)
    if features.get("schema_change", 0) > 0 or features.get("qt_score", 0) >= 8:
        ml_result = {"score": -0.9999, "level": "HIGH RISK", "status": "BLOCKED"}
        
    # Rule 2: Instant Veto for known injection signatures (UNION, Piggybacking)
    elif features.get("has_union", 0) > 0 or features.get("has_multi_statement", 0) > 0:
        ml_result = {"score": -0.8888, "level": "HIGH RISK", "status": "BLOCKED"}
        
    # Rule 3: Flag Suspicious Logic (Tautologies, excessive logic, deep nesting)
    elif "1=1" in q_upper or q_upper.count(" OR ") >= 2 or q_upper.count("SELECT") > 1:
        ml_result = {"score": -0.0450, "level": "MEDIUM RISK", "status": "FLAGGED"}
        
    # Rule 4: Pass everything else to the ML Model for behavioral analysis
    else:
        ml_result = predict_query_risk(feature_vector)
    # -----------------------------------
    
    q_type = q_upper.split()[0] if q_upper else "UNKNOWN"
    execution_time = round((time.time() - start_time) * 1000, 2)
    
    # 2. Log to Database
    log_entry = QueryLog(
        query_text=req.query,
        db_user=req.user,
        query_type=q_type,
        anomaly_score=ml_result["score"],
        status=ml_result["status"],
        execution_time=execution_time
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    # 3. Create Alert if Suspicious
    if ml_result["status"] in ["BLOCKED", "FLAGGED"]:
        # Generate the explanation using our new GenAI layer
        ai_explanation = generate_explanation(
            query=req.query,
            score=ml_result["score"],
            user=req.user,
            features=features
        )

        alert = Alert(
            query_id=log_entry.id,
            risk_level=ml_result["level"],
            explanation=ai_explanation
        )
        db.add(alert)
        db.commit()

    return {
        "id": log_entry.id,
        "status": ml_result["status"],
        "risk_level": ml_result["level"],
        "score": ml_result["score"],
        "execution_time_ms": execution_time
    }

@router.get("/activity")
def get_activity(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(limit).all()

@router.get("/alerts")
def get_alerts(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Alert).order_by(Alert.created_at.desc()).limit(limit).all()