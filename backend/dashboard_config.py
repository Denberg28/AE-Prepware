"""Read server-only dashboard settings without requiring a secrets file locally."""
import os
import streamlit as st


def setting(name, default=''):
    """Streamlit Secrets take priority; environment variables remain supported."""
    try:
        value = st.secrets.get(name)
    except FileNotFoundError:
        value = None
    if value is None:
        value = os.environ.get(name, default)
    return value.strip() if isinstance(value, str) else ''
