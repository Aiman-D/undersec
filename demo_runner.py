#!/usr/bin/env python3
"""
UnderSec Live Multi-Layer Demo Runner
Simulates comprehensive security traffic and telemetry across all 4 UnderSec layers:
1. PostgreSQL Wire Protocol Queries (DPI AST inspection & Isolation Forest scoring)
2. Panasonic Showroom Hardware Health Telemetry (Interactive vehicle configurator displays)
3. YOLOv8 CCTV Showroom Zone-Intrusion events
4. Real-Time XGBoost Chrome Phishing Extension scans
5. Automated Ollama LLM Multi-Layer Incident Summarization
"""

import requests
import time
import random
import sys

BASE_URL = "http://localhost:8000/api"

NORMAL_QUERIES = [
    "SELECT id, model_name, price FROM vehicles WHERE status = 'available';",
    "SELECT * FROM showroom_inventory WHERE location = 'Zone 1' AND stock > 0;",
    "SELECT count(*) FROM configurator_sessions WHERE created_at > '2026-04-01';",
    "SELECT id, battery_pct, temp_c FROM telemetry_logs WHERE vin = 'JTDKN3DU' LIMIT 1;",
    "UPDATE displays SET status = 'HEALTHY' WHERE id = 1;",
    "INSERT INTO configurator_sessions (vin, user_id, status) VALUES ('JTDKN3', 42, 'active');",
    "SELECT u.id, u.name, o.price FROM users u JOIN orders o ON u.id = o.user_id;",
    "SELECT AVG(temp_c) FROM telemetry_logs GROUP BY location;"
]

MALICIOUS_QUERIES = [
    "SELECT * FROM users WHERE username = 'admin' OR 1=1 --",
    "DROP TABLE vehicle_telemetry;",
    "SELECT * FROM accounts WHERE id = 1 UNION SELECT password, username FROM users;",
    "TRUNCATE TABLE query_logs;",
    "UPDATE users SET role = 'superadmin' WHERE id = 42 OR 1=1;",
    "SELECT * FROM products WHERE name = '' OR '' = '';",
    "SELECT * FROM orders; DROP TABLE displays; --"
]

PHISHING_URLS = [
    "http://secure-login-apple-update.com/verify?token=94812",
    "https://paypal.security-check-2023.net/login/auth.php",
    "http://192.168.1.55/admin/panasonic_kiosk_login.php",
    "http://netflix.account-billing-update.info/",
    "http://panasonic-showroom-kiosk-override.cfd/auth"
]

SAFE_URLS = [
    "https://panasonic.com/global",
    "https://na.panasonic.com/us/automotive-solutions",
    "https://github.com/Aiman-D/undersec",
    "https://toyota.com/crown",
    "https://lexus.com/models/RX"
]

SHOWROOM_DISPLAYS = ["PAN-CFG-01", "PAN-CFG-02", "PAN-CFG-03", "PAN-CFG-04", "PAN-CFG-05"]
SHOWROOM_FAULTS = ["gpu_thermal", "touch_lag", "chassis_tamper", "frame_drop"]
CCTV_ZONES = ["ZONE-01-CONCEPT", "ZONE-02-PROXY-CORE"]

def send_sql_query(query, user="showroom_kiosk"):
    try:
        res = requests.post(f"{BASE_URL}/query", json={"query": query, "user": user}, timeout=3)
        data = res.json()
        status = data.get("status", "UNKNOWN")
        level = data.get("risk_level", "")
        score = data.get("score", 0.0)
        print(f"  [Layer 1 · HTTP Gateway] {status:7s} ({level}) | Score: {score:7.4f} | {query[:45]}...")
    except Exception as e:
        print(f"  [Layer 1 · HTTP Gateway] Error: {e}")

def send_tcp_wire_query(query, port=5432):
    """Sends raw PostgreSQL v3 wire protocol query directly over TCP socket to the proxy."""
    import socket
    import struct
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.5)
    target_port = port
    try:
        try:
            s.connect(("127.0.0.1", port))
        except OSError:
            target_port = 9000
            s.connect(("127.0.0.1", target_port))
            
        # 1. Send StartupMessage (v3)
        startup = struct.pack("!II", 8, 196608)
        s.sendall(startup)
        
        # Read AuthOk + ReadyForQuery
        s.recv(1024)
        
        # 2. Send Query message ('Q')
        q_bytes = query.encode('utf-8') + b'\x00'
        q_pkt = b'Q' + struct.pack("!I", len(q_bytes) + 4) + q_bytes
        s.sendall(q_pkt)
        
        resp = s.recv(1024)
        if resp.startswith(b'E'):
            print(f"  [Layer 1 · TCP Wire Socket :{target_port}] BLOCKED & DROPPED SQLi socket | {query[:45]}...")
        else:
            print(f"  [Layer 1 · TCP Wire Socket :{target_port}] ALLOWED wire packet | {query[:45]}...")
            try:
                s.sendall(b'X\x00\x00\x00\x04')
            except Exception:
                pass
    except Exception:
        # Fallback to HTTP API query if TCP proxy port is unavailable
        send_sql_query(query)
    finally:
        s.close()

def trigger_showroom_telemetry():
    try:
        res = requests.get(f"{BASE_URL}/health/showroom/fleet", timeout=3)
        fleet = res.json()
        score = fleet.get("fleet_health_score", 100)
        h = fleet.get("counts", {}).get("healthy", 0)
        w = fleet.get("counts", {}).get("warning", 0)
        c = fleet.get("counts", {}).get("critical", 0)
        print(f"  [Layer 2 · Panasonic Telemetry] Fleet Score: {score}% | {h} Healthy, {w} Warning, {c} Critical")
        
        # 10% chance to simulate a hardware fault on an interactive configurator display
        if random.random() < 0.2:
            disp = random.choice(SHOWROOM_DISPLAYS)
            fault = random.choice(SHOWROOM_FAULTS)
            requests.post(f"{BASE_URL}/health/showroom/fault", json={
                "display_id": disp,
                "fault_type": fault,
                "duration_seconds": 12.0
            }, timeout=2)
            print(f"  [Layer 2 · Fault Injected] Injected {fault} on {disp} (Vehicle Configurator)")
    except Exception as e:
        print(f"  [Layer 2 · Panasonic Telemetry] Error: {e}")

def trigger_cctv_zone_event():
    try:
        zone = random.choice(CCTV_ZONES)
        res = requests.post(f"{BASE_URL}/cctv/trigger", json={"zone_id": zone, "duration_seconds": 8.0}, timeout=3)
        print(f"  [Layer 3 · YOLOv8 CCTV] Perimeter Intrusion Triggered in {zone}!")
    except Exception as e:
        print(f"  [Layer 3 · YOLOv8 CCTV] Error: {e}")

def send_phishing_check(url):
    try:
        res = requests.post(f"{BASE_URL}/phishing/analyze", json={"url": url}, timeout=4)
        data = res.json()
        status = data.get("status", "UNKNOWN")
        score = data.get("score", 0.0)
        print(f"  [Layer 4 · XGBoost Phishing] {status:7s} ({score:5.1f}%) | {url}")
    except Exception as e:
        print(f"  [Layer 4 · XGBoost Phishing] Error: {e}")

def fetch_incident_summary():
    try:
        res = requests.get(f"{BASE_URL}/incidents/summary", timeout=6)
        data = res.json()
        summary = data.get("summary", {})
        provider = summary.get("provider", "Ollama")
        threat = summary.get("threat_level", "NORMAL")
        briefing = summary.get("executive_summary", "")
        print(f"\n  ================================================================")
        print(f"  [GenAI Executive Briefing · {provider}] Threat: {threat}")
        print(f"  {briefing}")
        print(f"  ================================================================\n")
    except Exception as e:
        print(f"  [GenAI Summarizer] Error: {e}")

if __name__ == "__main__":
    print("\n==================================================================")
    print("  UnderSec 4-Layer Enterprise & Showroom Security Suite")
    print(f"  Connecting to UnderSec Gateway at: {BASE_URL}")
    print("==================================================================\n")
    
    # Check if backend is alive
    try:
        requests.get("http://localhost:8000/", timeout=2)
        print("✓ Connected to FastAPI backend.")
    except Exception:
        print("✗ Could not connect to FastAPI at http://localhost:8000.")
        print("  Please start the backend: cd backend && uvicorn main:app --reload")
        sys.exit(1)

    step = 0
    while True:
        step += 1
        print(f"\n--- [Cycle #{step}] Generating Multi-Layer Security Activity ---")
        
        # 1. Database Queries (Interleaves TCP wire socket queries and REST Gateway queries)
        is_normal = (random.random() < 0.7)
        q = random.choice(NORMAL_QUERIES if is_normal else MALICIOUS_QUERIES)
        user = "panasonic_kiosk_app" if is_normal else "threat_actor_42"
        if random.random() < 0.5:
            send_tcp_wire_query(q)
        else:
            send_sql_query(q, user=user)
            
        # 2. Showroom Hardware Telemetry
        trigger_showroom_telemetry()
        
        # 3. Occasional CCTV Zone Intrusion
        if random.random() < 0.25:
            trigger_cctv_zone_event()
            
        # 4. Phishing Checks
        if random.random() < 0.5:
            url = random.choice(PHISHING_URLS if random.random() < 0.5 else SAFE_URLS)
            send_phishing_check(url)
            
        # 5. Every 5 cycles, query the Ollama AI incident summarizer
        if step % 5 == 0:
            fetch_incident_summary()
            
        time.sleep(random.uniform(1.5, 3.0))
