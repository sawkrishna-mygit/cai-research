"""
Streamlit Cloud entry point (repo root).
Deploy with main file: streamlit_app.py
"""
import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_PLATFORM = _ROOT / "cai_platform"
if str(_PLATFORM) not in sys.path:
    sys.path.insert(0, str(_PLATFORM))

_APP = _PLATFORM / "app_streamlit.py"
_spec = importlib.util.spec_from_file_location("cai_app_streamlit", _APP)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
