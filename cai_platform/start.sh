#!/usr/bin/env bash
# Start CAI Research Portfolio (static site) and Streamlit Playground locally.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if ! python3 -c "import streamlit" 2>/dev/null; then
  echo "Installing dependencies..."
  python3 -m pip install -q -r requirements.txt
fi

if [ ! -f "web/assets/data/systems.json" ]; then
  echo "Generating web data and figures..."
  python3 export_web_data.py
  python3 generate_figures.py
fi

cleanup() {
  echo ""
  echo "Stopping servers..."
  kill "$WEB_PID" "$STREAMLIT_PID" 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM

echo "Starting portfolio site on http://localhost:8080"
(cd web && python3 -m http.server 8080) &
WEB_PID=$!

echo "Starting Streamlit Playground on http://localhost:8501"
python3 -m streamlit run app_streamlit.py --server.headless true --server.port 8501 &
STREAMLIT_PID=$!

sleep 2
if ! kill -0 "$STREAMLIT_PID" 2>/dev/null; then
  echo "ERROR: Streamlit failed to start. Try manually:"
  echo "  cd \"$ROOT\" && python3 -m streamlit run app_streamlit.py"
  kill "$WEB_PID" 2>/dev/null || true
  exit 1
fi

echo ""
echo "CAI Platform is running:"
echo "  Portfolio:   http://localhost:8080"
echo "  Playground:  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both."

wait
