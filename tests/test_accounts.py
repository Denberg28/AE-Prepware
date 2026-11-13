import json
import sqlite3
import httpx
import pytest
from fastapi.testclient import TestClient
from backend.api import create_app
from backend.bank import load_bank

NUMBER='AE-1234567890123456'
CODE='a1'*32

@pytest.fixture
def service(tmp_path, monkeypatch):
    for name in ('GEMINI_API_KEY','GEMINI_MODEL','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):
        monkeypatch.delenv(name,raising=False)
    now=[1_794_567_600.0];path=tmp_path/'accounts.sqlite'
    return TestClient(create_app(db_path=path,clock=lambda:now[0])),path,now

def register(client,number=NUMBER,code=CODE,name='Test Cadet'):
    r=client.post('/accounts/register',json={'number':number,'recovery':code,'name':name})
    assert r.status_code==201,r.text
    return r.json(),{'Authorization':'Bearer '+r.json()['token']}

def result(sid='math',session='test-session'):
    bank=load_bank();items=[q for q in bank['questions'] if q['subject']==sid][:50]
    return {'id':session,'bankVersion':bank['version'],'subject':sid,'answers':[{'id':q['id'],'choice':q['answer'] if i%2==0 else (q['answer']+1)%4} for i,q in enumerate(items)]}

def test_recoverable_identity_hashing_and_token_expiry(service):
    client,path,now=service;a,h=register(client)
    assert a['number']==NUMBER and a['history']==[]
    assert 'recovery' not in a and 'recovery_hash' not in a
    assert client.post('/accounts/login',json={'number':NUMBER,'recovery':'b2'*32}).status_code==401
    login=client.post('/accounts/login',json={'number':NUMBER,'recovery':CODE})
    assert login.status_code==200 and login.json()['number']==NUMBER
    again,_=register(client);assert again['number']==NUMBER
    with sqlite3.connect(path) as c:
        row=c.execute('SELECT salt,recovery_hash FROM study_accounts').fetchone()
        assert row[0] and row[1]!=CODE
        assert c.execute('SELECT token_hash FROM account_tokens LIMIT 1').fetchone()[0]!=a['token']
    now[0]+=30*86400+1
    assert client.get('/accounts/me',headers=h).status_code==401

def test_server_grade_retry_conflict_account_isolation_and_leaderboard(service):
    client,path,now=service;_,h=register(client)
    body=result();r=client.post('/accounts/results',json=body,headers=h)
    assert r.status_code==200,r.text
    assert r.json()['correct']==25 and r.json()['credited']==25
    assert client.post('/accounts/results',json=body,headers=h).json()==r.json()
    changed=json.loads(json.dumps(body));changed['answers'][0]['choice']=1
    assert client.post('/accounts/results',json=changed,headers=h).status_code==409
    profile=client.get('/accounts/me',headers=h).json()
    assert len(profile['history'])==1 and sum(x['seen'] for x in profile['stats'].values())==50
    # Another session may repeat practice, but it cannot farm unique daily points.
    body['id']='session-two';r=client.post('/accounts/results',json=body,headers=h)
    assert r.json()['credited']==0
    other,other_h=register(client,'AE-0000000000000001','c3'*32,'Other Cadet')
    assert client.get('/accounts/me',headers=other_h).json()['history']==[]
    assert client.post('/accounts/results',json={**body,'account':NUMBER},headers=other_h).status_code==422
    board=client.get('/accounts/leaderboard').json()['entries']
    assert board[0]['points']==25 and board[0]['attempts']==100
    assert 'number' not in board[0] and 'accountNumber' not in board[0]
    assert board[0]['accountSuffix']==NUMBER[-4:]
    # Restore on a new device yields the same results and progress.
    restored=client.post('/accounts/login',json={'number':NUMBER,'recovery':CODE}).json()
    assert len(restored['history'])==2 and sum(x['correct'] for x in restored['stats'].values())==50

def test_result_validation_rejects_duplicate_mixed_unknown_and_fabricated_score(service):
    client,_,_=service;_,h=register(client)
    body=result()
    bad=json.loads(json.dumps(body));bad['answers'][1]=bad['answers'][0]
    assert client.post('/accounts/results',json=bad,headers=h).status_code==422
    bad=json.loads(json.dumps(body));bad['answers'][0]['id']='AD001'
    assert client.post('/accounts/results',json=bad,headers=h).status_code==422
    for invalid in [True,4,'0']:
        bad=json.loads(json.dumps(body));bad['answers'][0]['choice']=invalid
        assert client.post('/accounts/results',json=bad,headers=h).status_code==422
    assert client.post('/accounts/results',json={**body,'score':50},headers=h).status_code==422
    assert client.post('/accounts/results',json={**body,'bankVersion':'unknown'},headers=h).status_code==409
    assert client.post('/accounts/results',json={**body,'answers':body['answers'][:-1]},headers=h).status_code==422
    assert client.post('/accounts/results',json=body).status_code==401
    assert client.get('/accounts/me',headers=h).json()['history']==[]

def test_deletion_cascades_and_logout_revokes_token(service):
    client,path,_=service;_,h=register(client)
    client.post('/accounts/results',json=result(),headers=h)
    assert client.post('/accounts/logout',headers=h).status_code==200
    assert client.get('/accounts/me',headers=h).status_code==401
    token=client.post('/accounts/login',json={'number':NUMBER,'recovery':CODE}).json()['token']
    assert client.post('/accounts/delete',headers={'Authorization':'Bearer '+token}).status_code==200
    assert client.get('/accounts/leaderboard').json()['entries']==[]
    with sqlite3.connect(path) as c:
        for table in ('study_accounts','study_results','account_tokens','account_progress','account_credits'):
            assert c.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]==0

def test_ai_topic_selection_uses_only_allowlisted_topics_and_never_answers(service,monkeypatch):
    client,_,_=service;_,h=register(client);original=load_bank()
    fallback=client.post('/accounts/plan',json={'subject':'math','ai':True},headers=h).json()
    assert fallback['selection']=='adaptive-fallback' and len(set(fallback['ids']))==50
    monkeypatch.setenv('GEMINI_API_KEY','fake-provider-test-key')
    calls=[]
    original_post=httpx.Client.post
    def provider_post(self,url,**kwargs):
        if 'generativelanguage.googleapis.com' not in str(url):
            return original_post(self,url,**kwargs)
        calls.append(kwargs)
        prompt=kwargs['json']['contents'][0]['parts'][0]['text']
        assert NUMBER not in prompt and CODE not in prompt and 'Test Cadet' not in prompt
        return httpx.Response(200,request=httpx.Request('POST',url),json={'candidates':[{'content':{'parts':[{'text':'["Derivatives"]'}]}}]})
    monkeypatch.setattr(httpx.Client,'post',provider_post)
    chosen=client.post('/accounts/plan',json={'subject':'math','ai':True},headers=h).json()
    assert chosen['selection']=='ai-assisted' and len(set(chosen['ids']))==50
    assert chosen['topics']==['Derivatives'] and len(calls)==1
    assert all(i.startswith('MA') for i in chosen['ids'])
    assert load_bank()==original

def test_ai_malformed_or_quota_failure_falls_back(service,monkeypatch):
    client,_,_=service;_,h=register(client);monkeypatch.setenv('GEMINI_API_KEY','fake-key')
    original_post=httpx.Client.post
    mode=[200]
    def provider_post(self,url,**kwargs):
        if 'generativelanguage.googleapis.com' not in str(url):
            return original_post(self,url,**kwargs)
        return httpx.Response(mode[0],request=httpx.Request('POST',url),json={'candidates':[{'content':{'parts':[{'text':'["invented topic"]'}]}}]})
    monkeypatch.setattr(httpx.Client,'post',provider_post)
    for status in (200,429):
        mode[0]=status;r=client.post('/accounts/plan',json={'subject':'math','ai':True},headers=h)
        assert r.status_code==200 and r.json()['selection']=='adaptive-fallback'
        assert len(set(r.json()['ids']))==50
