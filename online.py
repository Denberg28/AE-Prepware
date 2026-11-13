"""One persistent host: AE sync API at root, Streamlit faculty UI at /dashboard."""
from pathlib import Path
import os
import streamlit as st
from fastapi.responses import RedirectResponse
from backend.dashboard_config import setting

for name in ('AE_DB','AE_BANK','AE_ENROLLMENT_CODE','AE_FACULTY_SYNC_KEY','AE_ALLOW_PRIVATE_BANK_SYNC','GEMINI_API_KEY','GEMINI_MODEL'):
    value=setting(name)
    if value:os.environ[name]=value

from backend.api import create_app
dashboard=st.App(Path(__file__).parent/'backend/dashboard.py')
app=create_app(lifespan=dashboard.lifespan())
app.mount('/dashboard',dashboard)

@app.get('/')
def root():return RedirectResponse('/dashboard/')

if __name__=='__main__':
    import uvicorn
    uvicorn.run('online:app',host='0.0.0.0',port=int(os.getenv('PORT','8501')),workers=1)
