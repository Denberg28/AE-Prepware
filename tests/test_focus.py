import copy
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api import create_app
from backend.bank import load_bank, validate_bank
from backend.authoring import compatible_refresh
from scripts.curate_prc_bank import curate
from scripts.audit_prc_focus import audit


def test_curation_is_reproducible_append_only_and_no_new_ai():
    bank=load_bank()
    policy=json.loads(Path('docs/prc-focus-policy.json').read_text())
    old=copy.deepcopy(bank)
    old.pop('focus');old.pop('extends',None);old['version']='historical-input'
    old['questions'][[q['id'] for q in old['questions']].index('ST005')].pop('active',None)
    new=curate(old,policy,'new-version')
    assert len(new['questions'])==len(old['questions'])==360
    assert len(new['focus']['questions'])==120
    assert compatible_refresh(old,new)==new
    assert new['focus']==bank['focus']
    report=audit(Path('app/src/main/assets/bank.json'))
    assert report['numericCheckCount']==77 and report['expandedNumericCheckCount']==264
    assert all(sum(a['examItems'] for a in bank['focus']['areas'].values() if a['subject']==s)==50 for s in ('math','aero','structures','construction','powerplant','ethics'))
    for mutation in (lambda b:b['focus']['questions'].update(UNKNOWN={'area':'math-1'}),lambda b:b['focus']['questions']['MA001'].update(area='aero-1'),lambda b:b['questions'][0].update(active=False)):
        bad=copy.deepcopy(bank);mutation(bad)
        with pytest.raises(ValueError,match='Core'):validate_bank(bad)


def test_core_plan_20_result_retries_and_full_50_compatibility(tmp_path):
    client=TestClient(create_app(tmp_path/'focus.sqlite'))
    account=client.post('/accounts/register',json={'number':'AE-1234567890123456','name':'Core Cadet','recovery':'a'*64}).json()
    auth={'Authorization':'Bearer '+account['token']};bank=load_bank();index={q['id']:q for q in bank['questions']}
    plan=client.post('/accounts/plan',json={'subject':'aero','scope':'focus'},headers=auth)
    assert plan.status_code==200,plan.text
    ids=plan.json()['ids'];assert len(set(ids))==20 and set(ids)<=set(bank['focus']['questions'])
    payload={'id':'core-session','bankVersion':bank['version'],'subject':'aero','answers':[{'id':i,'choice':index[i]['answer']} for i in ids]}
    result=client.post('/accounts/results',json=payload,headers=auth)
    assert result.status_code==200 and result.json()['correct']==result.json()['total']==20
    assert client.post('/accounts/results',json=payload,headers=auth).json()==result.json()
    assert sum(x['seen'] for x in client.get('/accounts/me',headers=auth).json()['stats'].values())==20
    assert len(client.post('/accounts/plan',json={'subject':'aero'},headers=auth).json()['ids'])==50
    assert client.post('/accounts/results',json={**payload,'id':'invalid-length','answers':payload['answers'][:-1]},headers=auth).status_code==422
    assert client.post('/accounts/plan',json={'subject':'math','scope':'focus','sourceMode':'IN'},headers=auth).status_code==409


def test_private_core_hybrid_keeps_exact_10_each_and_original_three_choices(tmp_path):
    bank=load_bank(); bank.update(version='synthetic-private-focus',extends=bank['version'],distribution='private-study')
    for i,q in enumerate([x for x in bank['questions'] if x['subject']=='aero'][:20]):
        item={**copy.deepcopy(q),'id':f'TEST-IN-{i}','origin':'IN','prompt':'Synthetic fixture: '+q['prompt'],'choices':q['choices'][:3],
              'review':'source-key-verified','reviewer':'Automated TEST FIXTURE',
              'upload':{'file':'synthetic.json','locator':str(i),'rights':'user-provided-private','sha256':'a'*64,'key':'A','keyPage':1}}
        bank['questions'].append(item);bank['focus']['questions'][item['id']]={'area':'aero-2'}
    target=tmp_path/'private.json';target.write_text(json.dumps(bank));client=TestClient(create_app(tmp_path/'private.sqlite',target))
    token=client.post('/accounts/register',json={'number':'AE-1234567890123456','name':'Private Cadet','recovery':'b'*64}).json()['token'];auth={'Authorization':'Bearer '+token}
    r=client.post('/accounts/plan',json={'subject':'aero','scope':'focus','sourceMode':'hybrid'},headers=auth)
    assert r.status_code==200,r.text
    assert len(r.json()['ids'])==20 and sum(i.startswith('TEST-IN-') for i in r.json()['ids'])==10
    index={q['id']:q for q in bank['questions']};payload={'id':'hybrid-core','subject':'aero','bankVersion':bank['version'],'answers':[{'id':i,'choice':index[i]['answer']} for i in r.json()['ids']]}
    assert client.post('/accounts/results',json=payload,headers=auth).json()['correct']==20
    payload['answers'][next(i for i,a in enumerate(payload['answers']) if a['id'].startswith('TEST-IN-'))]['choice']=3;payload['id']='fabricated-D'
    assert client.post('/accounts/results',json=payload,headers=auth).status_code==422
