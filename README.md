<div align="center">
  <img src="https://img.icons8.com/color/96/000000/shield.png" alt="Undersec Logo" />
  <h1>Undersec Security Suite</h1>
  <p><b>An infrastructure security tool featuring a custom PostgreSQL TCP proxy (DPI), a YOLO-based CCTV anomaly engine, and an ML-powered Phishing detection extension.</b></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" alt="Python 3.12">
    <img src="https://img.shields.io/badge/FastAPI-0.104.1-00a393?style=for-the-badge&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/YOLOv8-Computer_Vision-FF9900?style=for-the-badge&logo=opencv" alt="YOLOv8">
    <img src="https://img.shields.io/badge/XGBoost-Machine_Learning-FF5A5F?style=for-the-badge" alt="XGBoost">
    <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" alt="React">
  </p>
</div>

<br/>

## 🚀 Features

Undersec is a multi-faceted security suite built to protect the modern enterprise.

### 1. Database Security Gateway (TCP Proxy)
- **Zero-Latency Custom Postgres Proxy**: Parses PostgreSQL v3 Wire Protocol using `asyncio` for zero-latency, in-memory query interception.
- **Deep Packet Inspection (DPI)**: Analyzes queries using Abstract Syntax Tree (AST) parsing with `sqlparse` to prevent sophisticated SQL injections and unauthorized schema changes.
- **Inline Machine Learning Inference**: Embeds an Isolation Forest model directly in the proxy loop to detect anomalies without HTTP round-trip latency.
- **GenAI Alert Summarization**: Fire-and-forget integration with local LLMs (Ollama) via background tasks for automated, real-time incident response summarization.

### 2. Physical Security (CCTV Engine)
- **Computer Vision Inference**: Utilizes the `Ultralytics YOLOv8` model for real-time person and object detection on CCTV feeds.
- **Zone Intrusion Detection**: Generates anomaly scores and alerts based on spatial bounding-box rules (e.g., unauthorized personnel detected in restricted zones).

### 3. Client Security (Phishing Extension)
- **XGBoost Phishing Model**: A trained XGBoost model that extracts 7 heuristic features (entropy, IP presence, subdomain depth, etc.) from URLs to detect phishing sites.
- **Chrome Extension integration**: Instantly scores sites in real-time as the user navigates, blocking high-risk interactions before credentials can be stolen.

## 🧠 Architecture Highlights

Unlike standard CRUD applications, Undersec operates at the network and physical layer:

- **Network Layer**: Intercepts the standard Postgres client (e.g. `psql`, `pgAdmin`) and reads `StartupMessage` and `Query` packets directly from the TCP socket byte stream. Drops malicious connections with an `ErrorResponse` (type `E`) packet.
- **Computer Vision**: Leverages PyTorch-based YOLO inference to convert raw image frames into actionable security intelligence.
- **Machine Learning Layer**: Uses Isolation Forest for Database queries and XGBoost for Phishing URLs.

## 🛠️ Tech Stack

- **ML & CV**: `scikit-learn`, `xgboost`, `ultralytics (YOLO)`, `opencv`
- **Proxy**: Python, `asyncio`, `sqlparse`
- **Backend**: FastAPI, SQLAlchemy, SQLite
- **Frontend**: React, Recharts
- **Testing**: `pytest`, `pytest-asyncio`

## 🏃 Getting Started

### 1. Backend & Proxy
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the API Backend
uvicorn main:app --reload

# In a new terminal, start the TCP Proxy
python tcp_proxy.py
```

### 2. Frontend
```bash
cd frontend
npm install
npm start
```

### 3. Generate Traffic
```bash
# Run the demo runner to simulate normal and malicious database traffic
python demo_runner.py
```

## 🧪 Testing

Undersec includes a robust `pytest` suite for the `feature_extractor` and `postgres_parser`.
```bash
cd backend
PYTHONPATH=. pytest tests/
```

## 🛡️ License
MIT License