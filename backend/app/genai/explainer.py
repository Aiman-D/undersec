import requests
import os
import json
import time

# Default to local Ollama.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_NAME = os.getenv("LLM_MODEL", "llama3")

def generate_explanation(query: str, score: float, user: str, features: dict) -> str:
    """Explains a single SQL injection or database anomaly."""
    prompt = f"""Explain why this database query is suspicious. 
Query: {query}
Score: {score}
User: {user}
Features: {features}

Give a concise security explanation in 1 to 2 sentences max."""

    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=4)
        if response.status_code == 200:
            resp_text = response.json().get("response", "").strip()
            if resp_text:
                return resp_text
    except Exception:
        pass

    # Deterministic Rule-Based Fallback
    explanation = "Suspicious database pattern detected. "
    if features.get("qt_score", 0) >= 8:
        explanation += "Contains destructive DDL commands (DROP/ALTER). "
    elif features.get("qt_score", 0) >= 5:
        explanation += "Contains high-risk bulk deletion commands. "
        
    if features.get("has_union", 0) > 0:
        explanation += "Detected UNION token pattern characteristic of data exfiltration SQLi. "
    if features.get("schema_change", 0) > 0:
        explanation += "Attempted unauthorized database schema mutation. "
    if features.get("has_multi_statement", 0) > 0:
        explanation += "Piggybacked multiple statements (;) identified. "

    if explanation == "Suspicious database pattern detected. ":
        explanation += "Query syntax and token complexity heavily deviates from normal user baselines."

    return explanation.strip()

def summarize_incidents_with_ollama(incidents: list) -> dict:
    """
    Unified 4-Layer Incident Summarization using Ollama LLM.
    Correlates Database DPI attacks, Panasonic Showroom hardware alerts,
    CCTV zone intrusions, and Phishing telemetry into an executive security briefing.
    """
    if not incidents:
        return {
            "provider": "Ollama / UnderSec Intelligence",
            "model": MODEL_NAME,
            "threat_level": "LOW",
            "executive_summary": "All 4 UnderSec security layers (PostgreSQL DPI, Panasonic Telemetry, YOLOv8 CCTV, XGBoost Phishing) report normal operational baselines with zero active threats.",
            "correlated_layers": [],
            "action_items": ["Continue automated telemetry and wire packet monitoring."],
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    prompt = f"""You are UnderSec Lead Security AI Officer. Analyze the following multi-layer security incidents across our 4 layers:
(1) PostgreSQL Wire Protocol TCP Proxy (DPI / Isolation Forest)
(2) Panasonic Showroom Hardware Health Telemetry (Interactive Vehicle Displays)
(3) YOLOv8 CCTV Zone-Intrusion Engine
(4) Real-Time XGBoost Chrome Phishing Extension

Incidents:
{json.dumps(incidents, indent=2)}

Provide a concise, professional executive incident summary. 
Address:
1. Threat Severity & Affected Layers
2. Attack Correlation & Potential Coordinated Breach Intent
3. Actionable Containment Steps for Security Ops
Keep the response under 150 words."""

    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=5)
        if response.status_code == 200:
            llm_text = response.json().get("response", "").strip()
            if llm_text:
                return {
                    "provider": "Local Ollama LLM",
                    "model": MODEL_NAME,
                    "threat_level": "HIGH" if any(i.get("severity") in ["CRITICAL", "HIGH", "HIGH RISK"] for i in incidents) else "MEDIUM",
                    "executive_summary": llm_text,
                    "correlated_layers": list(set(i.get("layer", "Unknown") for i in incidents)),
                    "total_incidents": len(incidents),
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }
    except Exception:
        pass

    # Intelligent Structured Fallback Engine
    layers_hit = list(set(i.get("layer", "Unknown") for i in incidents))
    has_critical = any(i.get("severity") in ["CRITICAL", "HIGH RISK", "ALERT"] for i in incidents)
    threat_level = "CRITICAL" if has_critical and len(layers_hit) > 1 else "HIGH" if has_critical else "ELEVATED"
    
    summary_parts = []
    summary_parts.append(f"Security Alert: UnderSec detected {len(incidents)} anomalous event(s) across {len(layers_hit)} subsystem(s): {', '.join(layers_hit)}.")
    
    # Analyze database events
    db_events = [i for i in incidents if i.get("layer") == "Layer 1 - Database Proxy"]
    if db_events:
        summary_parts.append(f"Database Gateway dropped {len(db_events)} SQLi attempt(s) via deep AST packet inspection & Isolation Forest anomaly isolation.")
        
    # Analyze showroom hardware
    hw_events = [i for i in incidents if i.get("layer") == "Layer 2 - Panasonic Showroom Telemetry"]
    if hw_events:
        summary_parts.append(f"Showroom telemetry flagged {len(hw_events)} hardware diagnostic anomaly on interactive vehicle-configurator displays.")

    # Analyze CCTV
    cctv_events = [i for i in incidents if i.get("layer") == "Layer 3 - YOLOv8 CCTV Engine"]
    if cctv_events:
        summary_parts.append(f"YOLOv8 vision perimeter engine detected {len(cctv_events)} zone breach(es) around restricted concept vehicle stages.")

    # Analyze Phishing
    phish_events = [i for i in incidents if i.get("layer") == "Layer 4 - XGBoost Phishing Guard"]
    if phish_events:
        summary_parts.append(f"Chrome Phishing extension intercepted {len(phish_events)} malicious URL navigation attempt(s).")

    summary_parts.append("Recommendation: Enforce socket disconnection, inspect physical showroom display enclosures, and alert physical security dispatch.")
    
    return {
        "provider": "UnderSec Multi-Layer Rule Fallback (Ollama Offline)",
        "model": "Deterministic Hybrid Classifier",
        "threat_level": threat_level,
        "executive_summary": " ".join(summary_parts),
        "correlated_layers": layers_hit,
        "total_incidents": len(incidents),
        "action_items": [
            "Maintain TCP socket block on offending database clients",
            "Dispatch technician to inspect Panasonic showroom display chassis switches",
            "Review camera CAM-04 recording at concept vehicle perimeter",
            "Block identified phishing domain on enterprise DNS firewall"
        ],
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }