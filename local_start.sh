#!/bin/bash
# Local Execution Script for Pinterest Hunter

echo "======================================"
echo " Starting Pinterest Hunter Locally! "
echo "======================================"

# CLEANUP: Kill any zombie processes still hanging on the ports
echo "[*] Cleaning up existing processes on 8080 and 3000..."
# Aggressively kill using both port lookups and process patterns
lsof -ti :8080 | xargs kill -9 2>/dev/null
lsof -ti :3000 | xargs kill -9 2>/dev/null
pkill -9 -f uvicorn 2>/dev/null
pkill -9 -f "next-dev" 2>/dev/null
sleep 1

# Start the Python Backend API in the background
echo "[*] Spinning up Python FastAPI Backend on Port 8080..."
cd backend || exit
if [ -f "../.venv/bin/activate" ]; then
    source ../.venv/bin/activate
    echo "[*] Environment [.venv] activated successfully."
else
    echo "[!] ERROR: .venv not found. Running with global python..."
fi

uvicorn main:app --host 0.0.0.0 --port 8080 --reload &

# Start the Next.js UI
echo "[*] Spinning up Next.js Website on Port 3000..."
export PATH=$PATH:/usr/local/bin
cd ../frontend || exit
npm run dev
