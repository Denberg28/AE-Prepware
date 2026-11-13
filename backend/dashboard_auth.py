"""Server-side faculty edit gate; student accounts never grant edit permission."""
import hashlib
import re
import secrets
import time

import streamlit as st

from .authoring import verify_password
from .dashboard_config import setting


def admin_gate():
    username = setting('AE_ADMIN_USERNAME')
    encoded = setting('AE_ADMIN_PASSWORD_HASH')
    legacy_number = setting('AE_ADMIN_NUMBER')
    legacy_recovery = re.sub(r'[\s-]', '', setting('AE_ADMIN_RECOVERY')).lower()
    legacy = not username and not encoded and bool(re.fullmatch(r'AE-\d{16}', legacy_number)) and bool(re.fullmatch(r'[a-f0-9]{64}', legacy_recovery))
    if legacy:
        username = legacy_number
        encoded = hashlib.sha256(legacy_recovery.encode()).hexdigest()
    if not username or not encoded:
        st.info('Admin editing is disabled. Configure AE_ADMIN_USERNAME and AE_ADMIN_PASSWORD_HASH in server Secrets to enable it.')
        return False
    fingerprint = hashlib.sha256((username + encoded).encode()).hexdigest()
    session = st.session_state.get('admin_session', {})
    if session.get('fingerprint') == fingerprint and time.time() < session.get('expires', 0):
        st.caption('Signed in as admin · ' + username)
        if st.button('Sign out admin'):
            del st.session_state.admin_session
            st.rerun()
        return True
    with st.form('admin_login', clear_on_submit=True):
        st.subheader('Admin sign in')
        login = st.text_input('Admin account number' if legacy else 'Admin username', max_chars=100)
        password = st.text_input('Admin recovery code' if legacy else 'Admin password', type='password', max_chars=1024)
        submit = st.form_submit_button('Sign in admin')
    if submit:
        now = time.time()
        attempts = [t for t in st.session_state.get('admin_attempts', []) if now-t < 900]
        if len(attempts) >= 5:
            st.error('Too many attempts in this session. Wait 15 minutes before retrying.')
        elif login.strip() == username and (secrets.compare_digest(hashlib.sha256(re.sub(r'[\s-]', '', password).lower().encode()).hexdigest(), encoded) if legacy else verify_password(password, encoded)):
            st.session_state.admin_session = {'fingerprint': fingerprint, 'expires': now + 3600}
            st.session_state.admin_attempts = []
            st.rerun()
        else:
            st.session_state.admin_attempts = [*attempts, now]
            st.error('Admin credentials are incorrect.')
    return False
