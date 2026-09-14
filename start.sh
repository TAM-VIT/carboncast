#!/usr/bin/env bash
# CarbonCast - one command to run the booth demo. No internet required.
set -e
cd "$(dirname "$0")/backend"

if [ ! -f artifacts/models.pkl ]; then
  echo "[1/3] No model found. Training (about 20s)..."
  python3 train.py
fi
if [ ! -f artifacts/precomputed.json ]; then
  echo "[2/3] Precomputing optimiser results (about 60s)..."
  python3 precompute.py
fi
if [ ! -f ../frontend/dist/index.html ]; then
  echo "[!] Frontend not built. Run: cd frontend && npm install && npm run build"
  exit 1
fi

echo "[3/3] Starting CarbonCast on http://localhost:8000"
pkill -f "uvicorn app:app" 2>/dev/null || true
sleep 1
python3 -m uvicorn app:app --port 8000 --host 127.0.0.1 &
PID=$!
for i in $(seq 1 30); do
  curl -s -o /dev/null http://127.0.0.1:8000/api/meta && break
  sleep 1
done
echo ""
echo "  ==> CarbonCast is live at http://localhost:8000"
echo "  ==> Press Ctrl+C to stop."
echo ""
open http://localhost:8000 2>/dev/null || true
wait $PID
