import copy
import json
import sqlite3
import pytest
from fastapi.testclient import TestClient
from backend.api import create_app
from backend.bank import load_bank,validate_bank

@pytest.fixture
def cohort(tmp_path):
    now=[1_794_567_600.0]
    db=tmp_path/'test.sqlite'
    app=create_app(db_path=db,clock=lambda:now[0])
    return TestClient(app),db,now

def join(client,name='Cadet One'):
    r=client.post('/participants',json={'name':name});assert r.status_code==201,r.text
    return r.json(),{'Authorization':'Bearer '+r.json()['token']}

def test_server_grades_idempotently_and_hides_keys(cohort):
    client,db,now=cohort;account,headers=join(client)
    r=client.post('/challenges',json={},headers=headers);assert r.status_code==201
    c=r.json();assert len(c['questions'])==20;assert all('answer' not in q and 'explanation' not in q for q in c['questions'])
    again=client.post('/challenges',json={},headers=headers).json();assert again['id']==c['id']
    body={'answers':[{'id':q['id'],'choice':0} for q in c['questions']]}
    first=client.post('/challenges/'+c['id']+'/submit',json=body,headers=headers);assert first.status_code==200,first.text
    assert first.json()['score']==20;assert first.json()['credited']==20
    repeat=client.post('/challenges/'+c['id']+'/submit',json=body,headers=headers);assert repeat.json()==first.json()
    ranked=client.get('/leaderboard').json()['entries'];assert ranked[0]['points']==20;assert ranked[0]['attempts']==20
    with sqlite3.connect(db) as conn:
        stored=conn.execute('SELECT token_hash FROM participants').fetchone()[0];assert stored!=account['token'];assert len(stored)==64

def test_duplicate_unknown_and_bad_choices_are_rejected(cohort):
    client,_,_=cohort;_,h=join(client);c=client.post('/challenges',headers=h,json={}).json()
    url='/challenges/'+c['id']+'/submit'
    duplicate={'answers':[{'id':c['questions'][0]['id'],'choice':0}]*20}
    assert client.post(url,json=duplicate,headers=h).status_code==422
    for bad in [4,-1,'0',True]:
        body={'answers':[{'id':q['id'],'choice':bad} for q in c['questions']]}
        assert client.post(url,json=body,headers=h).status_code==422
    assert client.post('/challenges',json={}).status_code==401

def test_other_participant_cannot_submit_and_deletion_cascades(cohort):
    client,db,_=cohort;a,h=join(client);_,other=join(client,'Other Cadet');c=client.post('/challenges',headers=h,json={}).json()
    body={'answers':[{'id':q['id'],'choice':0} for q in c['questions']]}
    assert client.post('/challenges/'+c['id']+'/submit',json=body,headers=other).status_code==404
    assert client.post('/challenges/'+c['id']+'/submit',json=body,headers=h).status_code==200
    assert client.post('/participants/delete',json={},headers=h).status_code==200
    assert client.post('/challenges',json={},headers=h).status_code==401
    assert client.get('/leaderboard').json()['entries']==[]
    with sqlite3.connect(db) as conn:
        for table in ('challenges','credits','submissions'):assert conn.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]==0

def test_credit_is_once_per_question_per_server_day(cohort):
    client,_,now=cohort;_,h=join(client)
    expected=set()
    for _ in range(3):
        c=client.post('/challenges',headers=h,json={}).json();expected.update(q['id'] for q in c['questions'])
        client.post('/challenges/'+c['id']+'/submit',headers=h,json={'answers':[{'id':q['id'],'choice':0} for q in c['questions']]})
    assert client.get('/leaderboard').json()['entries'][0]['points']==len(expected)
    now[0]+=86401
    c=client.post('/challenges',headers=h,json={}).json()
    result=client.post('/challenges/'+c['id']+'/submit',headers=h,json={'answers':[{'id':q['id'],'choice':0} for q in c['questions']]}).json()
    assert result['credited']==20

def test_expiration_limits_and_oversized_request(cohort):
    client,_,now=cohort;_,h=join(client);c=client.post('/challenges',headers=h,json={}).json();now[0]+=86401
    body={'answers':[{'id':q['id'],'choice':0} for q in c['questions']]}
    assert client.post('/challenges/'+c['id']+'/submit',headers=h,json=body).status_code==410
    assert client.post('/participants',content='x'*17000).status_code==413
    for _ in range(60):join(client)
    assert client.post('/participants',json={'name':'Another'}).status_code==429

def test_bank_schema_gates_drafts_and_wrong_blueprint():
    bank=load_bank();assert len(bank['questions'])==72
    with pytest.raises(ValueError):validate_bank(bank,imported=True)
    bank=copy.deepcopy(bank);bank['subjects'][0]['weight']=25
    with pytest.raises(ValueError):validate_bank(bank)

def test_cors_only_trusted_app_origin(cohort):
    client,_,_=cohort
    good=client.options('/participants',headers={'Origin':'https://appassets.androidplatform.net','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'})
    assert good.headers['access-control-allow-origin']=='https://appassets.androidplatform.net'
    bad=client.options('/participants',headers={'Origin':'https://evil.example','Access-Control-Request-Method':'POST'})
    assert 'access-control-allow-origin' not in bad.headers
