#!/usr/bin/env bash
# Start only the Streamlit Analysis Playground.

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if ! python3 -c "import streamlit" 2>/dev/null; then
  echo "Installing dependencies..."
  python3 -m pip install -q -r requirements.txt
fi

echo "Starting Streamlit Playground on http://localhost:8501"
exec python3 -m streamlit run app_streamlit.py --server.port 8501
