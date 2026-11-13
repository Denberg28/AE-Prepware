"""Streamlit Community Cloud entry point; run from the repository root."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parent / 'backend/dashboard.py'), run_name='__main__')
