"""Exercise the real Cloud entry and secret-to-request path without provider calls."""
from pathlib import Path
import httpx
import pytest
from streamlit.testing.v1 import AppTest
from backend.dashboard_config import setting

ENTRY = Path(__file__).resolve().parents[1] / 'streamlit_app.py'


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    for name in ('GEMINI_API_KEY', 'GEMINI_MODEL', 'AE_API_URL'):
        monkeypatch.delenv(name, raising=False)
    # Provider requests are mocked; host proxy configuration must not affect them.
    for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'):
        monkeypatch.delenv(name, raising=False)


def draft_button(app):
    return next(b for b in app.button if b.label == 'Draft a coursework plan with AI')


def test_settings_fall_back_without_secrets_file(monkeypatch):
    class MissingSecrets:
        def get(self, name):
            raise FileNotFoundError()
    monkeypatch.setattr('backend.dashboard_config.st.secrets', MissingSecrets())
    monkeypatch.setenv('GEMINI_API_KEY', '  environment-test-key  ')
    assert setting('GEMINI_API_KEY') == 'environment-test-key'
    assert setting('GEMINI_MODEL', 'default-model') == 'default-model'


def test_cloud_entry_without_key_keeps_local_workflow():
    app = AppTest.from_file(str(ENTRY)).run()
    assert not app.exception
    assert len(app.tabs) == 4
    assert draft_button(app).disabled
    assert any('AI is not configured' in item.value for item in app.info)


def test_faculty_monitoring_requires_admin_signin(monkeypatch):
    from backend.authoring import password_hash
    monkeypatch.setenv('AE_ADMIN_USERNAME','test-facilitator')
    monkeypatch.setenv('AE_ADMIN_PASSWORD_HASH',password_hash('test-readiness-password'))
    app=AppTest.from_file(str(ENTRY)).run()
    assert not app.exception
    assert any('Sign in under Question review' in x.value for x in app.info)
    assert not any(getattr(x,'label','')=='Student readiness reports' for x in app.get('file_uploader'))
    next(x for x in app.text_input if x.label=='Admin username').set_value('test-facilitator')
    next(x for x in app.text_input if x.label=='Admin password').set_value('test-readiness-password')
    next(b for b in app.button if b.label=='Sign in admin').click().run()
    assert not app.exception
    assert any(getattr(x,'label','')=='Student readiness reports' for x in app.get('file_uploader'))
    key='test-faculty-secret-'+'a'*32
    monkeypatch.setenv('AE_API_URL','https://cohort.example.com')
    monkeypatch.setenv('AE_FACULTY_SYNC_KEY',key)
    calls=[]
    def get(url,**kwargs):
        calls.append((url,kwargs))
        return httpx.Response(200,request=httpx.Request('GET',url),json={'entries':[{'Alias':'Student A','Subjects checked':3}]})
    monkeypatch.setattr(httpx,'get',get)
    next(b for b in app.button if b.label=='Sync online readiness summaries').click().run()
    assert not app.exception and len(calls)==1
    assert calls[0][0]=='https://cohort.example.com/faculty/monitoring'
    assert calls[0][1]['headers']['Authorization']=='Bearer '+key
    assert app.session_state['online_readiness'][0]['Alias']=='Student A'
    assert key not in str(app.main)


def test_cloud_secrets_reach_request_and_key_stays_off_ui(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY', 'unused-environment-key')
    calls = []
    def post(client, url, **kwargs):
        calls.append((url, kwargs))
        return httpx.Response(200, request=httpx.Request('POST', url), json={
            'candidates': [{'content': {'parts': [{'text': 'DRAFT FOR INSTRUCTOR REVIEW: Test plan'}]}}]
        })
    monkeypatch.setattr(httpx.Client, 'post', post)
    app = AppTest.from_file(str(ENTRY))
    app.secrets['GEMINI_API_KEY'] = 'cloud-test-key-never-display'
    app.secrets['AE_API_URL'] = 'https://cohort.example.com'
    app.run()
    assert not app.exception
    assert not draft_button(app).disabled
    assert any(x.value == 'https://cohort.example.com' for x in app.text_input)
    draft_button(app).click().run()
    assert not app.exception
    assert len(calls) == 1
    assert calls[0][0].endswith('/models/gemini-3.5-flash-lite:generateContent')
    assert calls[0][1]['headers']['x-goog-api-key'] == 'cloud-test-key-never-display'
    assert app.session_state['ai_plan'].startswith('DRAFT FOR INSTRUCTOR REVIEW')
    assert 'cloud-test-key-never-display' not in str(app.main)
    assert any('instructor review required' in w.value for w in app.warning)


def test_secret_model_override_and_provider_failure_recover(monkeypatch):
    def post(client, url, **kwargs):
        assert url.endswith('/models/custom-available-model:generateContent')
        return httpx.Response(429, request=httpx.Request('POST', url))
    monkeypatch.setattr(httpx.Client, 'post', post)
    app = AppTest.from_file(str(ENTRY))
    app.secrets['GEMINI_API_KEY'] = 'test-key'
    app.secrets['GEMINI_MODEL'] = 'custom-available-model'
    app.run()
    draft_button(app).click().run()
    assert not app.exception
    assert any('could not be generated' in e.value for e in app.error)
    assert 'ai_plan' not in app.session_state
    assert any('A focused 25-minute session' in s.value for s in app.subheader)
