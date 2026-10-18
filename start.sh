#!/bin/bash

echo "=========================================================="
echo "Starting UnderSec 4-Layer Enterprise & Showroom Suite..."
echo "=========================================================="

# Cleanup handler on exit
trap 'kill $BACKEND_PID $PROXY_PID $FRONTEND_PID 2>/dev/null; exit' SIGINT SIGTERM EXIT

# 1. Start FastAPI Central Gateway
echo "[1/3] Starting FastAPI Central Gateway (Port 8000)..."
cd backend
uvicorn main:app --port 8000 &
BACKEND_PID=$!

# 2. Start PostgreSQL v3 Wire Protocol TCP Proxy
echo "[2/3] Starting PostgreSQL Wire DPI Proxy (Port 5432 / 9000)..."
python3 tcp_proxy.py &
PROXY_PID=$!

# 3. Start React Dashboard
echo "[3/3] Starting React Showroom Dashboard (Port 3000)..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "=========================================================="
echo "UnderSec Suite is operational:"
echo "  • FastAPI Central Gateway:   http://localhost:8000"
echo "  • PostgreSQL TCP DPI Proxy:  localhost:5432 (or 9000)"
echo "  • React Showroom Dashboard:  http://localhost:3000"
echo "  • Chrome Extension Folder:   ./extension"
echo "  • Traffic Generator:         python demo_runner.py"
echo "=========================================================="
echo "Press Ctrl+C to stop all services."

wait
