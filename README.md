<div align="center">
  <img src="https://img.icons8.com/color/96/000000/shield.png" alt="Undersec Logo" />
  <h1>Undersec Database Security Gateway</h1>
  <p><b>An infrastructure security tool featuring a custom asynchronous PostgreSQL TCP proxy for Real-time Deep Packet Inspection (DPI) and an LLM-based alert summarization pipeline.</b></p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" alt="Python 3.12">
    <img src="https://img.shields.io/badge/FastAPI-0.104.1-00a393?style=for-the-badge&logo=fastapi" alt="FastAPI">
    <img src="https://img.shields.io/badge/PostgreSQL-Proxy-336791?style=for-the-badge&logo=postgresql" alt="PostgreSQL Proxy">
    <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react" alt="React">
  </p>
</div>

<br/>

## 🚀 Features

- **Zero-Latency Custom Postgres TCP Proxy**: Parses PostgreSQL v3 Wire Protocol using `asyncio` for zero-latency, in-memory query interception.
- **Deep Packet Inspection (DPI)**: Analyzes queries using Abstract Syntax Tree (AST) parsing with `sqlparse` to prevent sophisticated SQL injections and unauthorized schema changes.
- **Inline Machine Learning Inference**: Embeds an Isolation Forest model directly in the proxy loop to detect anomalies without HTTP round-trip latency, ensuring zero performance degradation for safe queries.
- **GenAI Alert Summarization**: Fire-and-forget integration with local LLMs (Ollama) via background tasks for automated, real-time incident response summarization.

## 🧠 Architecture Highlights

Unlike standard CRUD applications, Undersec operates at the network level:

1. **Client Handshake**: Intercepts the standard Postgres client (e.g. `psql`, `pgAdmin`).
2. **Wire Protocol Decoding**: Reads `StartupMessage` and `Query` packets directly from the TCP socket byte stream.
3. **AST Tokenization**: Uses `sqlparse` to tokenize and walk the AST of intercepted queries.
4. **ML Scoring**: Feeds extracted features into an `IsolationForest` model.
5. **Enforcement**: 
    - **BLOCKED**: Drops the TCP connection immediately and sends an `ErrorResponse` (type `E`) to the Postgres client.
    - **ALLOWED**: Sends mock `CommandComplete` (type `C`) and `ReadyForQuery` (type `Z`) packets back to the client.
6. **Asynchronous Logging**: Spawns an `asyncio.create_task` HTTP request to the FastAPI backend to store the incident and generate a GenAI alert summary asynchronously.

## 🛠️ Tech Stack

- **Proxy / ML**: Python, `asyncio`, `scikit-learn`, `sqlparse`
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