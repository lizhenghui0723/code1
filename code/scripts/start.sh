#!/bin/bash
cd ../backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ../frontend && npm start &
FRONTEND_PID=$!
echo $BACKEND_PID > ../scripts/backend.pid
echo $FRONTEND_PID > ../scripts/frontend.pid
echo "后端和前端已启动。" 