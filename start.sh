#!/bin/bash

echo "Starting Undersec Security Gateway..."

# Navigate to backend, install new deps, and start FastAPI
echo "Setting up backend..."
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Navigate to frontend, install deps, and start React
echo "Setting up frontend..."
cd ../frontend
npm install
npm start &
FRONTEND_PID=$!

# Wait for user interrupt
echo "Both servers are running."
echo "Press Ctrl+C to stop both servers."
wait
