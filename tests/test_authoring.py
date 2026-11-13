"""Synthetic instructor fixtures never enter the bundled educational bank."""
import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

from backend.api import create_app
from backend.authoring import compatible_refresh, merge_instructor_upload, password_hash, revise_question, verify_password
from backend.bank import load_bank


def instructor_upload(count=50):
    bank = copy.deepcopy(load_bank())
    pool = [q for q in bank['questions'] if q['subject'] == 'aero'][:count]
    for i, q in enumerate(pool):
        q.update(id=f'TEST-IN-{i:03}', origin='IN', prompt='Synthetic instructor fixture: ' + q['prompt'],
                 review='approved', reviewer='Automated TEST FIXTURE',
                 upload={'file': 'synthetic-test.json', 'locator': f'Test item {i+1}', 'rights': 'instructor-original'})
    bank.update(version='test-upload', questions=pool)
    return bank


def revision(bank):
    q = bank['questions'][0]
    return revise_question(bank, q['id'], prompt=q['prompt'] + ' (reviewed fixture)', choices=q['choices'],
                           answer=1, explanation='Synthetic corrected explanation for automated regression.',
                           reviewer='Automated TEST FIXTURE', version='test-revision')


def test_correction_is_append_only_and_old_key_is_immutable():
    bank = load_bank()
    original = copy.deepcopy(bank)
    changed = revision(bank)
    assert bank == original
    assert changed['questions'][0]['answer'] == 0
    assert changed['questions'][0]['active'] is False
    assert changed['questions'][-1]['answer'] == 1
    assert changed['questions'][-1]['origin'] == 'AI'
    assert changed['questions'][-1]['supersedes'] == bank['questions'][0]['id']
    compatible_refresh(bank, changed)
    changed['questions'][0]['answer'] = 2
    with pytest.raises(ValueError, match='unchanged'):
        compatible_refresh(bank, changed)


def test_in_upload_approval_provenance_dedup_and_atomic_merge():
    bank = load_bank()
    original = copy.deepcopy(bank)
    upload = instructor_upload()
    merged = merge_instructor_upload(bank, upload, 'test-IN1')
    assert len(merged['questions']) == 410
    assert bank == original
    for mutate in (
        lambda q: q.update(review='pending'),
        lambda q: q.update(origin='AI'),
        lambda q: q['upload'].update(rights='unknown'),
        lambda q: q.update(id=bank['questions'][0]['id']),
    ):
        bad = copy.deepcopy(upload)
        mutate(bad['questions'][0])
        with pytest.raises(ValueError):
            merge_instructor_upload(bank, bad, 'invalid')
    duplicate = copy.deepcopy(upload)
    duplicate['questions'][1].update(prompt=duplicate['questions'][0]['prompt'], choices=duplicate['questions'][0]['choices'])
    with pytest.raises(ValueError, match='Duplicate active'):
        merge_instructor_upload(bank, duplicate, 'invalid')
    assert bank == original


def test_api_source_quota_and_archived_key_grading_after_restart(tmp_path):
    baseline = load_bank()
    database = tmp_path / 'cohort.sqlite'
    first = TestClient(create_app(database))
    account = {'number': 'AE-1234567890123456', 'name': 'Test Cadet', 'recovery': 'a'*64}
    token = first.post('/accounts/register', json=account).json()['token']
    auth = {'Authorization': 'Bearer ' + token}
    old_answers = [{'id': q['id'], 'choice': q['answer']} for q in baseline['questions'] if q['subject'] == 'math'][:50]
    changed = merge_instructor_upload(revision(baseline), instructor_upload(), 'test-combined')
    # Both operations form a single append-only refresh from baseline.
    changed['extends'] = baseline['version']
    target = tmp_path / 'bank.json'
    target.write_text(json.dumps(changed))
    second = TestClient(create_app(database, target))
    hybrid = second.post('/accounts/plan', json={'subject': 'aero', 'sourceMode': 'hybrid'}, headers=auth)
    assert hybrid.status_code == 200
    index = {q['id']: q for q in changed['questions']}
    assert sum(index[qid]['origin'] == 'IN' for qid in hybrid.json()['ids']) == 25
    assert second.post('/accounts/plan', json={'subject': 'math', 'sourceMode': 'IN'}, headers=auth).status_code == 409
    assert second.post('/accounts/plan', json={'subject': 'aero', 'sourceMode': 'invalid'}, headers=auth).status_code == 422
    result = second.post('/accounts/results', headers=auth, json={
        'id': 'queued-before-edit', 'bankVersion': baseline['version'], 'subject': 'math', 'answers': old_answers})
    assert result.status_code == 200
    assert result.json()['correct'] == 50
    assert result.json()['bankVersion'] == baseline['version']
    altered = copy.deepcopy(changed)
    altered['questions'][0]['answer'] = 2
    altered['questions'][0]['review'] = 'approved'
    altered['version'] = 'bad-new-version'
    target.write_text(json.dumps(altered))
    with pytest.raises(ValueError, match='archived question'):
        create_app(database, target)


def test_admin_password_and_real_dashboard_edit(monkeypatch):
    password = 'test-only-admin-password-123'
    encoded = password_hash(password)
    assert verify_password(password, encoded)
    assert not verify_password('wrong', encoded)
    assert not verify_password(password, 'bad-encoding')
    monkeypatch.setenv('AE_ADMIN_USERNAME', 'test-admin')
    monkeypatch.setenv('AE_ADMIN_PASSWORD_HASH', encoded)
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'streamlit_app.py')).run()
    assert not app.exception
    assert not any(b.label == 'Save reviewed revision' for b in app.button)
    next(x for x in app.text_input if x.label == 'Admin username').set_value('test-admin')
    next(x for x in app.text_input if x.label == 'Admin password').set_value('wrong')
    next(b for b in app.button if b.label == 'Sign in admin').click().run()
    assert any('incorrect' in e.value for e in app.error)
    assert not any(b.label == 'Save reviewed revision' for b in app.button)
    next(x for x in app.text_input if x.label == 'Admin username').set_value('test-admin')
    next(x for x in app.text_input if x.label == 'Admin password').set_value(password)
    next(b for b in app.button if b.label == 'Sign in admin').click().run()
    assert not app.exception
    next(x for x in app.text_area if x.label == 'Question text').set_value('Synthetic corrected question for browser regression?')
    next(x for x in app.selectbox if x.label == 'Correct answer').select(1)
    next(x for x in app.text_input if x.label == 'Instructor reviewer name').set_value('Automated TEST FIXTURE')
    next(x for x in app.checkbox if x.label.startswith('I independently')).check()
    next(b for b in app.button if b.label == 'Save reviewed revision').click().run()
    assert not app.exception
    bank = app.session_state['bank']
    assert len(bank['questions']) == 361
    assert bank['questions'][0]['active'] is False
    assert bank['questions'][-1]['answer'] == 1
    next(b for b in app.button if b.label == 'Sign out admin').click().run()
    assert not any(b.label == 'Save reviewed revision' for b in app.button)
