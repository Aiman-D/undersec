import pytest
import numpy as np
from fastapi.testclient import TestClient

from main import app
from app.db.database import init_db
from app.core.feature_extractor import extract_features, features_to_vector
from app.ml.predictor import predict_query_risk
from app.ml.phishing_model import extract_features as extract_phish_features, predict_phishing_risk
from app.ml.showroom_telemetry import (
    get_showroom_fleet_telemetry,
    get_display_detail,
    inject_display_fault,
    clear_display_fault,
    clear_all_display_faults
)
from app.ml.cctv_engine import (
    analyze_cctv_frame,
    get_annotated_jpeg_frame,
    trigger_cctv_intrusion,
    clear_cctv_intrusion,
    SHOWROOM_ZONES
)
from app.genai.explainer import generate_explanation, summarize_incidents_with_ollama

# Ensure test database tables are created
init_db()

client = TestClient(app)

# ----------------- LAYER 1: PostgreSQL DPI & Isolation Forest -----------------

def test_ast_deep_packet_inspection_drop_table():
    features = extract_features("DROP TABLE vehicle_telemetry;", "attacker_ip")
    assert features["schema_change"] == 5
    assert features["qt_score"] == 10

def test_ast_deep_packet_inspection_union_sqli():
    features = extract_features("SELECT * FROM configurator WHERE id = 1 OR 1=1 UNION SELECT password FROM admin;", "hacker")
    assert features["has_union"] == 3
    assert features["complexity"] > 0

def test_isolation_forest_scoring():
    safe_vec = [0, 0, 0, 0, 0, 0.69, 14.0, 1.0, 40, 0, 8]
    res_safe = predict_query_risk(safe_vec)
    assert res_safe["status"] in ["ALLOWED", "FLAGGED"]
    
    # Highly anomalous vector (schema destruction, huge rows, high complexity, union)
    bad_vec = [10, 5, 3, 3, 3, 10.5, 3.0, 1.0, 250, 8, 20]
    res_bad = predict_query_risk(bad_vec)
    assert res_bad["score"] < 0

def test_api_query_blocking():
    # Attempt SQL injection through API
    response = client.post("/api/query", json={
        "query": "SELECT * FROM users WHERE id = 1 UNION SELECT password FROM users;",
        "user": "sqli_bot"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "BLOCKED"
    assert data["risk_level"] == "HIGH RISK"

# ----------------- LAYER 2: Panasonic Showroom Hardware Telemetry -----------------

def test_showroom_fleet_telemetry():
    clear_all_display_faults()
    fleet = get_showroom_fleet_telemetry()
    assert fleet["total_displays"] == 5
    assert "displays" in fleet
    assert len(fleet["displays"]) == 5
    
    # Check diagnostics keys
    first = fleet["displays"][0]
    assert "fps" in first["diagnostics"]
    assert "gpu_temp_c" in first["diagnostics"]
    assert "panel_temp_c" in first["diagnostics"]
    assert "touch_latency_ms" in first["diagnostics"]
    assert "chassis_tamper" in first["diagnostics"]

def test_showroom_fault_injection_and_recovery():
    # Inject thermal throttling fault on PAN-CFG-01
    inject_res = inject_display_fault("PAN-CFG-01", "gpu_thermal", 15.0)
    assert inject_res["status"] == "fault_injected"
    
    detail = get_display_detail("PAN-CFG-01")
    assert detail["telemetry"]["status"] in ["WARNING", "CRITICAL"]
    assert detail["telemetry"]["diagnostics"]["gpu_temp_c"] > 85.0
    
    # Clear fault
    clear_display_fault("PAN-CFG-01")
    detail_cleared = get_display_detail("PAN-CFG-01")
    assert detail_cleared["telemetry"]["diagnostics"]["gpu_temp_c"] < 80.0

def test_api_showroom_fleet():
    response = client.get("/api/health/showroom/fleet")
    assert response.status_code == 200
    data = response.json()
    assert data["total_displays"] == 5
    assert "fleet_health_score" in data

# ----------------- LAYER 3: YOLOv8 CCTV Zone-Intrusion Engine -----------------

def test_cctv_zones_defined():
    assert len(SHOWROOM_ZONES) >= 3
    zone_ids = [z["id"] for z in SHOWROOM_ZONES]
    assert "ZONE-01-CONCEPT" in zone_ids
    assert "ZONE-02-PROXY-CORE" in zone_ids

def test_cctv_intrusion_detection_and_frame_gen():
    trigger_cctv_intrusion("ZONE-01-CONCEPT", 10.0)
    analysis = analyze_cctv_frame()
    assert analysis["has_breach"] is True
    assert analysis["status"] == "ALERT"
    assert analysis["anomaly_score"] > 70.0
    
    # Check JPEG frame generation
    jpeg = get_annotated_jpeg_frame()
    assert len(jpeg) > 1000
    assert jpeg[:2] == b'\xff\xd8' # Valid JPEG magic bytes

    clear_cctv_intrusion()

def test_api_cctv_endpoints():
    res_feed = client.get("/api/cctv/feed")
    assert res_feed.status_code == 200
    assert "detections" in res_feed.json()

    res_frame = client.get("/api/cctv/frame")
    assert res_frame.status_code == 200
    assert res_frame.headers["content-type"] == "image/jpeg"

# ----------------- LAYER 4: Real-Time XGBoost Phishing Detector -----------------

def test_extract_7_url_heuristic_features():
    url = "http://192.168.1.55/panasonic/login.php?session=abc"
    feats = extract_phish_features(url)
    assert len(feats) == 7
    # feats: [len_url, len_host, count_digits, subdomains, has_ip, non_alnum, ent]
    assert feats[4] == 1 # has_ip should be 1
    assert feats[0] > 0
    assert feats[1] > 0

def test_xgboost_phishing_inference():
    safe_res = predict_phishing_risk("https://panasonic.com/automotive")
    assert safe_res["status"] == "ALLOWED"
    assert safe_res["score"] < 40
    
    phish_res = predict_phishing_risk("http://192.168.1.100/panasonic/login.php")
    assert phish_res["status"] in ["FLAGGED", "BLOCKED"]
    assert phish_res["score"] > 50

def test_api_phishing_analyze():
    response = client.post("/api/phishing/analyze", json={
        "url": "http://panasonic-account-update.xyz/verify-login.php"
    })
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "features" in data
    assert len(data["features"]) == 7

# ----------------- Ollama Incident Summarization & Overview -----------------

def test_incident_summarization_fallback():
    incidents = [
        {"layer": "Layer 1 - Database Proxy", "severity": "HIGH RISK", "detail": "UNION injection dropped"},
        {"layer": "Layer 2 - Panasonic Showroom Telemetry", "severity": "CRITICAL", "detail": "GPU thermal throttling"},
        {"layer": "Layer 3 - YOLOv8 CCTV Engine", "severity": "ALERT", "detail": "Zone breach at Concept Car"},
        {"layer": "Layer 4 - XGBoost Phishing Guard", "severity": "HIGH RISK", "detail": "Phishing URL intercepted"}
    ]
    summary = summarize_incidents_with_ollama(incidents)
    assert "executive_summary" in summary
    assert "threat_level" in summary
    assert len(summary["correlated_layers"]) == 4

def test_api_overview_and_incidents():
    res_overview = client.get("/api/overview/status")
    assert res_overview.status_code == 200
    data = res_overview.json()
    assert "layer1_db_proxy" in data["layers"]
    assert "layer2_showroom_telemetry" in data["layers"]
    assert "layer3_cctv_engine" in data["layers"]
    assert "layer4_phishing_guard" in data["layers"]

    res_summary = client.get("/api/incidents/summary")
    assert res_summary.status_code == 200
    assert "summary" in res_summary.json()
