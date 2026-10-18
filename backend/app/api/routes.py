from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional, List
import time
import random
import requests

from app.db.database import get_db, SessionLocal
from app.db.models import QueryLog, Alert, SystemSettings
from app.core.feature_extractor import extract_features, features_to_vector
from app.ml.predictor import predict_query_risk
from app.genai.explainer import generate_explanation, summarize_incidents_with_ollama, OLLAMA_URL, MODEL_NAME
from app.ml.showroom_telemetry import get_showroom_fleet_telemetry
from app.ml.cctv_engine import analyze_cctv_frame
from app.api.phishing import RECENT_SCANS

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

class IncidentSummarizeRequest(BaseModel):
    incidents: Optional[List[dict]] = None

# Background task for GenAI query explanation
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

def collect_active_incidents(db: Session) -> list:
    """Collects multi-layer security incidents across all 4 UnderSec security layers."""
    incidents = []
    
    # 1. Layer 1: Recent Database DPI Alerts
    alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(5).all()
    for a in alerts:
        query_log = db.query(QueryLog).filter(QueryLog.id == a.query_id).first()
        incidents.append({
            "layer": "Layer 1 - Database Proxy",
            "type": "SQLi Injection Socket Drop",
            "severity": a.risk_level or "HIGH RISK",
            "timestamp": str(a.created_at),
            "detail": query_log.query_text if query_log else "Malicious SQL Payload",
            "explanation": a.explanation
        })
        
    # 2. Layer 2: Panasonic Showroom Hardware Diagnostics
    try:
        fleet = get_showroom_fleet_telemetry()
        for d in fleet.get("displays", []):
            if d.get("status") in ["WARNING", "CRITICAL"]:
                incidents.append({
                    "layer": "Layer 2 - Panasonic Showroom Telemetry",
                    "type": "Interactive Display Hardware Anomaly",
                    "severity": d["status"],
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d.get("timestamp", time.time()))),
                    "detail": f"{d['name']} ({d['id']}) - {', '.join(d.get('fault_reasons', ['Anomaly detected']))}",
                    "diagnostics": d.get("diagnostics")
                })
    except Exception as e:
        print(f"Error collecting showroom incidents: {e}")
        
    # 3. Layer 3: YOLOv8 CCTV Zone Intrusions
    try:
        cctv = analyze_cctv_frame()
        if cctv.get("has_breach"):
            for intr in cctv.get("intrusions", []):
                incidents.append({
                    "layer": "Layer 3 - YOLOv8 CCTV Engine",
                    "type": "Perimeter Zone Intrusion",
                    "severity": intr.get("severity", "HIGH"),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cctv.get("timestamp", time.time()))),
                    "detail": f"Unauthorized entry into {intr.get('zone_name')} (Anomaly Score: {intr.get('threat_score')})"
                })
    except Exception as e:
        print(f"Error collecting CCTV incidents: {e}")
        
    # 4. Layer 4: Real-time XGBoost Chrome Phishing Extension Scans
    for p in RECENT_SCANS[:5]:
        if p.get("status") in ["BLOCKED", "FLAGGED"]:
            incidents.append({
                "layer": "Layer 4 - XGBoost Phishing Guard",
                "type": "Phishing Credential Harvester",
                "severity": p.get("level", "HIGH RISK"),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.get("timestamp", time.time()))),
                "detail": f"URL {p['url']} scored {p['score']}% threat probability by XGBoost 7-feature model.",
                "reasons": p.get("reasons")
            })
            
    return incidents

@router.get("/incidents/summary")
async def get_incident_summary(db: Session = Depends(get_db)):
    """Returns an executive AI incident briefing correlating all 4 UnderSec security layers via Ollama LLM."""
    incidents = await run_in_threadpool(collect_active_incidents, db)
    summary = await run_in_threadpool(summarize_incidents_with_ollama, incidents)
    return {
        "summary": summary,
        "raw_incidents": incidents
    }

@router.post("/incidents/summarize")
async def summarize_custom_incidents(req: IncidentSummarizeRequest, db: Session = Depends(get_db)):
    """Summarizes specified or current security incidents using Ollama LLM."""
    if req.incidents is not None:
        incidents = req.incidents
    else:
        incidents = await run_in_threadpool(collect_active_incidents, db)
    summary = await run_in_threadpool(summarize_incidents_with_ollama, incidents)
    return {
        "summary": summary,
        "raw_incidents": incidents
    }

@router.get("/overview/status")
async def get_overview_status(db: Session = Depends(get_db)):
    """Unified status check across all 4 UnderSec layers and Ollama LLM."""
    def get_db_stats():
        total = db.query(QueryLog).count()
        blocked = db.query(QueryLog).filter(QueryLog.status == "BLOCKED").count()
        flagged = db.query(QueryLog).filter(QueryLog.status == "FLAGGED").count()
        alerts_count = db.query(Alert).count()
        return total, blocked, flagged, alerts_count
        
    total_q, blocked_q, flagged_q, alerts_count = await run_in_threadpool(get_db_stats)
    showroom = await run_in_threadpool(get_showroom_fleet_telemetry)
    cctv = await run_in_threadpool(analyze_cctv_frame)
    
    # Check Ollama status
    ollama_online = False
    try:
        r = requests.get(OLLAMA_URL.replace("/api/generate", "/api/tags"), timeout=1.0)
        ollama_online = (r.status_code == 200)
    except Exception:
        ollama_online = False
        
    phish_blocked = sum(1 for s in RECENT_SCANS if s["status"] == "BLOCKED")
    
    return {
        "timestamp": time.time(),
        "layers": {
            "layer1_db_proxy": {
                "name": "PostgreSQL v3 Wire Protocol TCP Proxy",
                "engine": "asyncio + sqlparse AST + Isolation Forest",
                "status": "ACTIVE",
                "port": 5432,
                "total_queries": total_q,
                "blocked_sockets": blocked_q,
                "flagged_queries": flagged_q,
                "alerts": alerts_count
            },
            "layer2_showroom_telemetry": {
                "name": "Panasonic Showroom Hardware Telemetry",
                "target": "Interactive Vehicle-Configurator Displays",
                "status": "MONITORING",
                "total_displays": showroom["total_displays"],
                "fleet_health_score": showroom["fleet_health_score"],
                "counts": showroom["counts"],
                "averages": showroom["averages"]
            },
            "layer3_cctv_engine": {
                "name": "YOLOv8 CCTV Zone-Intrusion Engine",
                "model": "Ultralytics YOLOv8n",
                "status": cctv["status"],
                "has_breach": cctv["has_breach"],
                "anomaly_score": cctv["anomaly_score"],
                "active_camera": cctv["camera_id"]
            },
            "layer4_phishing_guard": {
                "name": "XGBoost Chrome Phishing Extension",
                "model": "XGBoost Classifier (7 URL Features)",
                "status": "ONLINE",
                "features_tracked": 7,
                "scans_conducted": len(RECENT_SCANS),
                "phishing_blocked": phish_blocked
            }
        },
        "genai": {
            "engine": "Ollama LLM Incident Summarization",
            "model": MODEL_NAME,
            "ollama_online": ollama_online,
            "fallback_active": not ollama_online
        }
    }