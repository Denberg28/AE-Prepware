import copy
import json
import sqlite3
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from backend.api import create_app
from backend.bank import load_bank

NUMBER='AE-1234567890123456'

@pytest.fixture
def service(tmp_path,monkeypatch):
    for name in ('AE_ENROLLMENT_CODE','AE_ALLOW_PRIVATE_BANK_SYNC','AE_FACULTY_SYNC_KEY'):monkeypatch.delenv(name,raising=False)
    path=tmp_path/'sync.sqlite';bank=load_bank();clock=[1794628800.0]
    client=TestClient(create_app(path,clock=lambda:clock[0]))
    def register(number=NUMBER):
        r=client.post('/accounts/register',json={'number':number,'recovery':'a'*64,'name':'Cadet','rankOptIn':False})
        assert r.status_code==201,r.text
        return {'Authorization':'Bearer '+r.json()['token']}
    return client,path,bank,clock,register

def snapshot(bank):
    state={'schema':1,'name':'Cadet','accountNumber':NUMBER,'stats':{},'daily':{},'bookmarks':[],'flags':[],
           'history':[],'session':None,'selection':'adaptive','sourceMode':'AI','studyScope':'focus'}
    return {'operation':str(uuid.uuid4()),'expectedRevision':0,'bankVersion':bank['version'],'state':state,'share':False,'report':None}

def test_private_backup_retries_conflicts_isolation_and_deletion(service):
    client,path,bank,clock,register=service;auth=register();body=snapshot(bank)
    assert client.post('/accounts/snapshot',json=body).status_code==401
    assert client.get('/accounts/snapshot',headers=auth).json()=={'revision':0,'state':None}
    saved=client.post('/accounts/snapshot',json=body,headers=auth);assert saved.status_code==200,saved.text
    assert client.post('/accounts/snapshot',json=body,headers=auth).json()==saved.json()
    changed=copy.deepcopy(body);changed['state']['name']='Changed'
    assert client.post('/accounts/snapshot',json=changed,headers=auth).status_code==409
    changed['operation']=str(uuid.uuid4())
    assert client.post('/accounts/snapshot',json=changed,headers=auth).status_code==409
    changed['expectedRevision']=1
    assert client.post('/accounts/snapshot',json=changed,headers=auth).json()['revision']==2
    assert client.get('/accounts/snapshot',headers=auth).json()['state']['name']=='Changed'
    other=register('AE-0000000000000001')
    assert client.get('/accounts/snapshot',headers=other).json()['state'] is None
    assert client.post('/accounts/snapshot',json=body,headers=other).status_code==422
    assert client.post('/accounts/delete',headers=auth).status_code==200
    with sqlite3.connect(path) as db:
        for table in ('account_snapshots','sync_writes'):assert db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]==0

def test_server_grade_separate_from_backup_and_ranking_requires_consent(service):
    client,path,bank,clock,register=service;auth=register();items=[q for q in bank['questions'] if q['subject']=='aero'][:20]
    body={'id':'offline-1','bankVersion':bank['version'],'subject':'aero','answers':[{'id':q['id'],'choice':q['answer']} for q in items]}
    assert client.post('/accounts/results',json=body,headers=auth).json()['correct']==20
    assert client.get('/accounts/leaderboard').json()['entries']==[]
    assert client.post('/accounts/preferences',json={'rankOptIn':True},headers=auth).status_code==200
    assert client.get('/accounts/leaderboard').json()['entries'][0]['correct']==20
    assert client.post('/accounts/preferences',json={'rankOptIn':False},headers=auth).status_code==200
    assert client.get('/accounts/leaderboard').json()['entries']==[]
    assert len(client.get('/accounts/me',headers=auth).json()['history'])==1

def test_snapshot_validation_body_limits_and_unknown_versions(service):
    client,path,bank,clock,register=service;auth=register()
    for mutate in (
        lambda b:b['state'].update(cohort={'token':'secret'}),
        lambda b:b['state'].update(accountNumber='AE-0000000000000001'),
        lambda b:b['state'].update(stats={'unknown':{'seen':1,'correct':1,'streak':1,'last':1,'due':2}}),
        lambda b:b.update(share=True),
        lambda b:b['state'].update(history=[{'total':20,'correct':21}]),
    ):
        body=snapshot(bank);mutate(body)
        assert client.post('/accounts/snapshot',json=body,headers=auth).status_code==422
    body=snapshot(bank);body['bankVersion']='unknown'
    assert client.post('/accounts/snapshot',json=body,headers=auth).status_code==409
    assert client.post('/accounts/snapshot',content=b' '*1_000_001,headers=auth).status_code==413

def test_faculty_view_requires_secret_and_voluntary_sharing(service,monkeypatch):
    client,path,bank,clock,register=service;auth=register();body=snapshot(bank)
    report=json.loads(Path('tests/fixtures/readiness-report.json').read_text());clock[0]=report['generatedAt']/1000
    assert client.get('/faculty/monitoring').status_code==503
    key='private-faculty-key-'+'a'*32;monkeypatch.setenv('AE_FACULTY_SYNC_KEY',key)
    faculty={'Authorization':'Bearer '+key}
    assert client.get('/faculty/monitoring',headers=auth).status_code==401
    body.update(share=True,report=report)
    assert client.post('/accounts/snapshot',json=body,headers=auth).status_code==200
    data=client.get('/faculty/monitoring',headers=faculty).json()
    assert len(data['entries'])==1
    assert all(x not in json.dumps(data) for x in (NUMBER,'recovery','answer','token'))
    body.update(operation=str(uuid.uuid4()),expectedRevision=1,share=False,report=None)
    assert client.post('/accounts/snapshot',json=body,headers=auth).status_code==200
    assert client.get('/faculty/monitoring',headers=faculty).json()['entries']==[]

def test_bank_pull_auth_and_private_enrollment_barrier(service,monkeypatch,tmp_path):
    client,path,bank,clock,register=service;auth=register()
    assert client.get('/accounts/bank').status_code==401
    assert client.get('/accounts/bank',headers=auth).json()==bank
    private=copy.deepcopy(bank);private.update(version='private-test',distribution='private-study')
    target=tmp_path/'private.json';target.write_text(json.dumps(private));p=TestClient(create_app(tmp_path/'private.sqlite',target))
    assert p.post('/participants',json={'name':'Guest'}).status_code==403
    assert p.post('/challenges',json={}).status_code==403
    credentials={'number':NUMBER,'recovery':'a'*64,'name':'Cadet'}
    token=p.post('/accounts/register',json=credentials).json()['token'];h={'Authorization':'Bearer '+token}
    assert p.get('/accounts/bank',headers=h).status_code==403
    monkeypatch.setenv('AE_ALLOW_PRIVATE_BANK_SYNC','true')
    assert p.get('/accounts/bank',headers=h).status_code==403
    monkeypatch.setenv('AE_ENROLLMENT_CODE','class-enrollment-'+'a'*16)
    assert p.get('/accounts/bank',headers=h).status_code==403
    enrolled=p.post('/accounts/register',json={**credentials,'enrollment':'class-enrollment-'+'a'*16})
    assert enrolled.status_code==201
    h={'Authorization':'Bearer '+enrolled.json()['token']}
    assert p.get('/accounts/bank',headers=h).status_code==200
    assert p.post('/accounts/register',json={**credentials,'number':'AE-0000000000000001'}).status_code==403

def test_sync_tables_survive_restart(service):
    client,path,bank,clock,register=service;auth=register();body=snapshot(bank)
    assert client.post('/accounts/snapshot',json=body,headers=auth).status_code==200
    reopened=TestClient(create_app(path,clock=lambda:clock[0]))
    assert reopened.get('/accounts/snapshot',headers=auth).json()['state']==body['state']
