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
    
    # 1. Extract ML Features
    # Note: We mock rows_affected and time_of_day for real-time interception
    features = extract_features(req.query, req.user, time_of_day=14, rows_affected=1)
    feature_vector = features_to_vector(features)
    
    # 2. Score with Isolation Forest
    ml_result = predict_query_risk(feature_vector)
    
    # Determine basic query type for logging
    q_upper = req.query.upper()
    q_type = q_upper.split()[0] if q_upper else "UNKNOWN"
    
    execution_time = round((time.time() - start_time) * 1000, 2) # in ms
    
    # 3. Log to Database
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
    
    # 4. Create Alert if Suspicious
    # 4. Create Alert if Suspicious
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