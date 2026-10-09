#!/usr/bin/env bash
# JiraPilot AI - Complete System Runner Script (Linux/macOS)

echo "=========================================================="
echo "           JiraPilot AI — Starting Full Stack"
echo "=========================================================="

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# 1. Start Python AI Service on Port 8000
echo "[1/3] Starting Python AI Service on port 8000..."
cd "$DIR/ai-service" && uvicorn app.main:app --host 0.0.0.0 --port 8000 &
AI_PID=$!

# 2. Start Java Spring Boot Backend on Port 8080
echo "[2/3] Starting Spring Boot Backend on port 8080..."
cd "$DIR/backend" && mvn spring-boot:run &
BACKEND_PID=$!

# 3. Start React Frontend on Port 3000
echo "[3/3] Starting React Frontend on port 3000..."
cd "$DIR/frontend" && npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "=========================================================="
echo " All services started successfully!"
echo " - Frontend UI:        http://localhost:3000"
echo " - Backend API:        http://localhost:8080"
echo " - Python AI Service:  http://localhost:8000"
echo "=========================================================="

trap "kill $AI_PID $BACKEND_PID $FRONTEND_PID" EXIT
wait
