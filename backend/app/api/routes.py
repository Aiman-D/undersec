from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
import time
import random

from app.db.database import get_db, SessionLocal
from app.db.models import QueryLog, Alert, SystemSettings
from app.core.feature_extractor import extract_features, features_to_vector
from app.ml.predictor import predict_query_risk
from app.genai.explainer import generate_explanation

router = APIRouter()

def get_setting(db: Session, key: str, default: float) -> float:
    setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key).first()
    if not setting:
        setting = SystemSettings(setting_key=key, setting_value=default)
        db.add(setting)
        db.commit()
    return setting.setting_value

def set_setting(db: Session, key: str, value: float):
    setting = db.query(SystemSettings).filter(SystemSettings.setting_key == key).first()
    if not setting:
        setting = SystemSettings(setting_key=key, setting_value=value)
        db.add(setting)
    else:
        setting.setting_value = value
    db.commit()

class QueryRequest(BaseModel):
    query: str
    user: str = "app_user"

class ProxyLogRequest(BaseModel):
    query: str
    user: str
    q_type: str
    score: float
    status: str
    level: str
    execution_time_ms: float
    features: dict
    is_hardcoded: bool

# Background task for GenAI
def process_alert_background(query: str, fuzzed_score: float, user: str, features: dict, is_hardcoded: bool, log_entry_id: int, final_level: str):
    db = SessionLocal()
    try:
        ai_explanation = generate_explanation(
            query=query,
            score=fuzzed_score,
            user=user,
            features=features
        )
        if is_hardcoded:
            ai_explanation = f"[Policy Override] {ai_explanation}"

        alert = Alert(
            query_id=log_entry_id,
            risk_level=final_level,
            explanation=ai_explanation
        )
        db.add(alert)
        db.commit()
    finally:
        db.close()


@router.post("/query")
async def process_query(req: QueryRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    start_time = time.time()
    q_upper = req.query.upper()
    
    threshold = await run_in_threadpool(get_setting, db, "ml_block_threshold", -0.05)
    
    estimated_rows = 10000 if any(kw in q_upper for kw in ["DROP", "DELETE", "TRUNCATE", "ALTER"]) else 1
    
    # Run CPU-bound ML tasks in threadpool
    features = await run_in_threadpool(extract_features, req.query, req.user, 14, estimated_rows)
    feature_vector = await run_in_threadpool(features_to_vector, features)
    ml_result = await run_in_threadpool(predict_query_risk, feature_vector, threshold)
    
    fuzzed_score = round(ml_result["score"] + random.uniform(-0.005, 0.005), 4)
    
    final_status = ml_result["status"]
    final_level = ml_result["level"]
    is_hardcoded = False

    if features.get("schema_change", 0) > 0 or any(kw in q_upper for kw in ["DROP", "TRUNCATE", "ALTER"]):
        final_status = "BLOCKED"
        final_level = "HIGH RISK"
        is_hardcoded = True
    elif "UNION" in q_upper or "1=1" in q_upper or "--" in q_upper:
        final_status = "BLOCKED"
        final_level = "HIGH RISK"
        is_hardcoded = True
    elif q_upper.count(" OR ") >= 2 or q_upper.count("SELECT") > 1:
        if final_status != "BLOCKED":
            final_status = "FLAGGED"
            final_level = "MEDIUM RISK"
            is_hardcoded = True
            
    q_type = q_upper.split()[0] if q_upper else "UNKNOWN"
    execution_time = round((time.time() - start_time) * 1000, 2)
    
    # DB I/O in threadpool (since db session is sync)
    def save_log():
        log_entry = QueryLog(
            query_text=req.query,
            db_user=req.user,
            query_type=q_type,
            anomaly_score=fuzzed_score,
            status=final_status,
            execution_time=execution_time
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry.id
        
    log_id = await run_in_threadpool(save_log)
    
    if final_status in ["BLOCKED", "FLAGGED"]:
        # Offload GenAI entirely to background task
        background_tasks.add_task(
            process_alert_background,
            req.query, fuzzed_score, req.user, features, is_hardcoded, log_id, final_level
        )

    return {
        "id": log_id,
        "status": final_status,
        "risk_level": final_level,
        "score": fuzzed_score,
        "execution_time_ms": execution_time,
        "hardcoded_catch": is_hardcoded
    }

@router.post("/log_proxy_query")
async def log_proxy_query(req: ProxyLogRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    def save_log():
        log_entry = QueryLog(
            query_text=req.query,
            db_user=req.user,
            query_type=req.q_type,
            anomaly_score=req.score,
            status=req.status,
            execution_time=req.execution_time_ms
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry.id
        
    log_id = await run_in_threadpool(save_log)
    
    if req.status in ["BLOCKED", "FLAGGED"]:
        background_tasks.add_task(
            process_alert_background,
            req.query, req.score, req.user, req.features, req.is_hardcoded, log_id, req.level
        )
        
    return {"status": "logged", "id": log_id}

@router.get("/activity")
async def get_activity(limit: int = 50, db: Session = Depends(get_db)):
    def fetch():
        return db.query(QueryLog).order_by(QueryLog.timestamp.desc()).limit(limit).all()
    return await run_in_threadpool(fetch)

@router.get("/alerts")
async def get_alerts(limit: int = 50, db: Session = Depends(get_db)):
    def fetch():
        return db.query(Alert).order_by(Alert.created_at.desc()).limit(limit).all()
    return await run_in_threadpool(fetch)

@router.get("/settings")
async def get_settings_route(db: Session = Depends(get_db)):
    def fetch():
        return {
            "ml_block_threshold": get_setting(db, "ml_block_threshold", -0.05),
            "medium_rule_score": get_setting(db, "medium_rule_score", -0.0450)
        }
    return await run_in_threadpool(fetch)

@router.put("/settings")
async def update_settings(new_settings: dict, db: Session = Depends(get_db)):
    def update():
        for k, v in new_settings.items():
            set_setting(db, k, v)
        return new_settings
    return await run_in_threadpool(update)