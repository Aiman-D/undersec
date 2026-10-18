<div align="center">
  <img src="https://img.icons8.com/color/96/000000/shield.png" alt="UnderSec Logo" />
  <h1>UnderSec – 4-Layer Enterprise & Showroom Security Suite</h1>
  <p><b>Track Winner Apr 2026 · Multi-Modal Cyber-Physical Defense Infrastructure</b></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" alt="Python 3.12">
    <img src="https://img.shields.io/badge/FastAPI-0.104.1-00a393?style=for-the-badge&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/YOLOv8-Computer_Vision-FF9900?style=for-the-badge&logo=opencv" alt="YOLOv8">
    <img src="https://img.shields.io/badge/XGBoost-Machine_Learning-FF5A5F?style=for-the-badge&logo=xgboost" alt="XGBoost">
    <img src="https://img.shields.io/badge/Isolation_Forest-Scikit_Learn-orange?style=for-the-badge" alt="Isolation Forest">
    <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" alt="React">
    <img src="https://img.shields.io/badge/Ollama-Local_LLM-purple?style=for-the-badge" alt="Ollama">
  </p>
</div>

<br/>

## 🎯 Executive Overview

Modern enterprise and showroom environments face hybrid cyber-physical attack surfaces. Traditional firewalls operate only at network layers (L3/L4) or rely on rigid Web Application Firewall (WAF) regex rules, completely missing obfuscated database exfiltration, physical perimeter tampering, interactive kiosk degradation, and spear-phishing.

**UnderSec** is an end-to-end, 4-layer defense system purpose-built to safeguard enterprise infrastructure and interactive Panasonic vehicle-configurator showroom exhibits through inline AI inference, deep packet inspection, computer vision, and GenAI incident intelligence.

---

## 🛡️ The 4 Defense Layers

```
                                      ┌───────────────────────────────────────────────────────────────┐
                                      │             UnderSec Unified Security Suite                   │
                                      └───────────────────────────────┬───────────────────────────────┘
                                                                      │
            ┌──────────────────────────┬──────────────────────────────┴──────────────────────────────┬──────────────────────────┐
            ▼                          ▼                                                             ▼                          ▼
 ┌──────────────────────┐   ┌──────────────────────┐                                      ┌──────────────────────┐   ┌──────────────────────┐
 │       Layer 1        │   │       Layer 2        │                                      │       Layer 3        │   │       Layer 4        │
 │ PostgreSQL v3 Proxy  │   │  Panasonic Showroom  │                                      │     YOLOv8 CCTV      │   │  XGBoost Extension   │
 │   Wire DPI & AST     │   │  Hardware Telemetry  │                                      │    Zone-Intrusion    │   │  7 URL Heuristics    │
 └──────────┬───────────┘   └──────────┬───────────┘                                      └──────────┬───────────┘   └──────────┬───────────┘
            │                          │                                                             │                          │
            │ Drops SQLi Sockets       │ Monitors 3D FPS, GPU, Touch                                 │ Spatial Perimeter Bounds │ Real-Time Browser Guard
            │                          │                                                             │                          │
            └──────────────────────────┴──────────────────────────────┬──────────────────────────────┴──────────────────────────┘
                                                                      │
                                                                      ▼
                                                    ┌───────────────────────────────────┐
                                                    │   Unified FastAPI + React Hub     │
                                                    │  + Ollama LLM Incident Summarizer │
                                                    └───────────────────────────────────┘
```

### 1. PostgreSQL v3 Wire Protocol TCP Proxy (asyncio)
- **Zero-Latency In-Memory Packet Interception**: Listens on TCP port `5432` (or `9000`), parsing raw PostgreSQL v3 wire packets (`SSLRequest`, `StartupMessage`, `Query ('Q')`).
- **AST Deep Packet Inspection (DPI)**: Tokenizes query trees with `sqlparse` to detect nested comment bypasses, schema destruction (`DROP`, `ALTER`, `TRUNCATE`), multi-statement piggybacking, and `UNION` exfiltration tokens.
- **Inline Isolation Forest Inference**: Embeds trained `IsolationForest` scoring directly in the proxy loop. When anomaly thresholds are violated, the proxy immediately emits a `FATAL` error packet (`'E'`) and **drops the TCP client socket**.

### 2. Panasonic Showroom Hardware Health Telemetry
- **Interactive Vehicle-Configurator Fleet**: Tracks live diagnostic telemetry across 5 showroom display kiosks:
  - `PAN-CFG-01`: Main Pavilion - 8K Ultra-Wall Configurator (*Panasonic TH-98CQE2U / Lexus Concept Sport EV*)
  - `PAN-CFG-02`: EV Studio - 4K Interactive Touch Pod (*Panasonic TH-65SQE2W / Lexus RZ 450e SUV*)
  - `PAN-CFG-03`: VIP Bespoke Lounge - Dual Curved OLED Kiosk (*Panasonic TX-65MZ2000 Pro / Toyota Crown Signia*)
  - `PAN-CFG-04`: Materials & Trim Multi-Touch Table (*Panasonic Touch-Station Pro / Interior Finishes*)
  - `PAN-CFG-05`: Entrance Foyer - Interactive Portfolio Station (*Panasonic TH-55SQ2H / Commercial Signage*)
- **Telemetry Monitored**: 3D Unreal/WebGL viewport rendering FPS, GPU core thermal state (°C), panel backlight temperature (°C), capacitive multi-touch digitizer latency (ms), active touch points, HDMI 2.1 signal lock, and enclosure chassis tamper switches.
- **Fault Injection Sandbox**: Live simulation triggers for GPU thermal surge, touch digitizer lag, chassis tamper alerts, and frame crashes.

### 3. YOLOv8 CCTV Zone-Intrusion Engine
- **Perimeter & Physical Asset Protection**: Powered by `Ultralytics YOLOv8` with PyTorch 2.6 runtime compatibility.
- **Spatial Security Zones**:
  - `ZONE-01-CONCEPT`: Restricted Vehicle Stage (*Prototype Concept Car*)
  - `ZONE-02-PROXY-CORE`: UnderSec Gateway & Database Proxy Cabinet Enclosure (*Critical Infrastructure*)
  - `ZONE-03-CONFIGURATOR`: Customer Interactive Configurator Corridor (*Public Zone*)
- **Footprint Intersection Logic**: Evaluates ground-contact points against polygon zone boundaries to distinguish authorized showroom visitors from perimeter intruders, generating live annotated JPEG streams and anomaly scores.

### 4. Real-Time XGBoost Chrome Phishing Extension (7 URL Heuristic Features)
- **Trained Machine Learning Model**: Gradient boosted decision tree (`XGBClassifier`) evaluating **7 structural heuristic features**:
  1. `len_url`: Total URL length
  2. `len_host`: Hostname length
  3. `count_digits`: Total digits in URL
  4. `subdomains`: Subdomain count & depth
  5. `has_ip`: IP address host indicator (`1.0` or `0.0`)
  6. `non_alnum`: Ratio of non-alphanumeric special characters
  7. `path_entropy`: Shannon entropy of the URL path and query parameters
- **Manifest v3 Chrome Extension**: Background service worker inspecting active tabs in real-time, dynamically updating extension badges (`OK`, `WARN`, `DROP`) and providing a companion popup with visual feature breakdowns and sandbox scanning.

### 🤖 GenAI Incident Intelligence (Ollama LLM)
- Cross-correlates multi-layer incident telemetry across database socket drops, showroom hardware degradation, perimeter breaches, and phishing attacks.
- Synthesizes automated executive security briefings and immediate containment recommendations using local LLMs (Ollama `llama3`/`mistral`) with deterministic hybrid fallback.

---

## 🛠️ Tech Stack

| Domain | Technologies |
|---|---|
| **L1 Wire Proxy** | Python 3.12, `asyncio`, `struct`, `sqlparse`, `scikit-learn` (Isolation Forest) |
| **L2 Showroom Telemetry** | Python, FastAPI, NumPy, psutil, interactive diagnostic simulator |
| **L3 Vision Engine** | `ultralytics` (YOLOv8), `opencv-python-headless`, PyTorch 2.6 |
| **L4 Client Security** | `xgboost`, Chrome Extension (Manifest v3, Service Worker) |
| **GenAI Intelligence** | Ollama local LLM (`llama3`), background task correlation |
| **Backend API** | FastAPI, SQLAlchemy, SQLite, Pydantic, HTTPX |
| **Frontend** | React 19, Recharts, Lucide Icons, Modern Cyber-Dark CSS |

---

## 🏃 Getting Started

### 1. Backend & Proxy Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI Central Security Gateway
uvicorn main:app --reload --port 8000
```

In a separate terminal, start the PostgreSQL Wire Protocol TCP Proxy:
```bash
cd backend
python tcp_proxy.py
```
*The proxy will listen on `0.0.0.0:5432` (or fall back to port `9000` if 5432 is occupied).*

### 2. Frontend React Dashboard

```bash
cd frontend
npm install
npm start
```
*The dashboard opens at `http://localhost:3000`.*

### 3. Chrome Extension Installation

1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer mode** (toggle in top-right corner).
3. Click **Load unpacked** and select the `/extension` directory in this repository.
4. The **UnderSec Phishing Guard** icon will appear in your extensions bar, automatically inspecting active tabs via your local FastAPI engine.

### 4. Live Multi-Layer Demo Traffic Generator

To simulate real-time traffic across all 4 layers (queries, display telemetry, CCTV breaches, phishing checks, and Ollama incident briefings):
```bash
python demo_runner.py
```

---

## 🧪 Comprehensive Verification

UnderSec includes automated tests validating all 4 layers, model inference, and wire protocol socket behavior:

```bash
cd backend
PYTHONPATH=. pytest tests/ -v
```

### Verified Test Matrix:
- `test_ast_deep_packet_inspection_drop_table`: AST classification of destructive schema changes.
- `test_ast_deep_packet_inspection_union_sqli`: AST detection of `UNION` exfiltration tokens.
- `test_isolation_forest_scoring`: Verifies normal vs anomalous scoring separation.
- `test_tcp_proxy_drops_sqli_socket`: Proves TCP proxy immediately writes error packet and closes client socket on SQLi.
- `test_showroom_fleet_telemetry`: Verifies telemetry from all 5 Panasonic vehicle-configurator displays.
- `test_showroom_fault_injection_and_recovery`: Tests diagnostic fault injection and recovery.
- `test_cctv_intrusion_detection_and_frame_gen`: Validates YOLOv8 zone intrusion spatial detection and JPEG frame synthesis.
- `test_extract_7_url_heuristic_features`: Validates extraction of all 7 URL heuristic features.
- `test_xgboost_phishing_inference`: Tests trained XGBoost classifier on safe and phishing URLs.
- `test_incident_summarization_fallback`: Tests multi-layer Ollama incident summarization and structured fallback.

---

## 🛡️ License
MIT License · Built with rigor for the modern enterprise.