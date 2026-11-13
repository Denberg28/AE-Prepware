"""Original synthetic PDF fixtures verify column extraction without book content."""
import copy
import importlib.util
from pathlib import Path

import fitz
import pytest
from fastapi.testclient import TestClient

from backend.api import create_app
from backend.bank import load_bank, validate_bank

spec = importlib.util.spec_from_file_location('private_importer', Path(__file__).resolve().parents[1]/'scripts/import_private_guides.py')
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


def synthetic_pdf(path):
    doc = fitz.open()
    for index, left in enumerate((63, 27)):
        p = doc.new_page(width=603, height=774)
        p.insert_text((left, 70), 'Synthetic engineering topic', fontsize=15, fontname='hebo')
        for column in (0, 1):
            x = left + column*265.5
            number = 8001 + index*2 + column
            p.insert_text((x, 100), f'{number}. Original synthetic test question {number}?', fontsize=10)
            for row, letter in enumerate('ABC'):
                p.insert_text((x, 124+row*18), f'{letter}- Original option {letter}.', fontsize=10)
            p.insert_text((x, 198), 'Original explanation for this synthetic test.', fontsize=10, fontname='heit')
        p.insert_text((left, 714), 'Answers', fontsize=8)
        p.insert_text((left, 730), f'{8001+index*2} [B] (001) TEST    {8002+index*2} [C] (001) TEST', fontsize=8)
    doc.save(path)


def private_bank():
    b = copy.deepcopy(load_bank())
    b.update(distribution='private-study', version='synthetic-private')
    for i, q in enumerate([q for q in b['questions'] if q['subject']=='powerplant'][:50]):
        item=copy.deepcopy(q)
        item.update(id=f'TEST-IN-{i}', prompt=f'Synthetic three-choice item {i}: '+q['prompt'], choices=q['choices'][:3], origin='IN', review='source-key-verified',
                    upload={'file':'synthetic.pdf','locator':'Synthetic p1','rights':'user-provided-private','sha256':'a'*64,'key':'A','keyPage':1})
        b['questions'].append(item)
    return b


def test_mirrored_pdf_columns_choices_explanations_and_footer_keys(tmp_path):
    path=tmp_path/'synthetic.pdf'
    synthetic_pdf(path)
    accepted, held, report=importer.extract(path,'powerplant')
    assert report['sourceQuestions']==4
    assert not held
    assert [q['answer'] for q in accepted]==[1,2,1,2]
    assert all(len(q['choices'])==3 for q in accepted)
    assert all(q['explanation']=='Original explanation for this synthetic test.' for q in accepted)
    assert all('Original option C.' == q['choices'][2] for q in accepted)
    assert [q['upload']['keyPage'] for q in accepted]==[1,1,2,2]


def test_private_review_provenance_and_three_choice_server_grade(tmp_path):
    bank=private_bank()
    validate_bank(bank, imported=True, trusted=load_bank())
    invalid=copy.deepcopy(bank);invalid.pop('distribution')
    with pytest.raises(ValueError): validate_bank(invalid,imported=True,trusted=load_bank())
    invalid=copy.deepcopy(bank);invalid['questions'][-1]['upload']['key']='B'
    with pytest.raises(ValueError): validate_bank(invalid,imported=True,trusted=load_bank())
    path=tmp_path/'private.json';import json;path.write_text(json.dumps(bank))
    client=TestClient(create_app(tmp_path/'db.sqlite',path))
    data=client.post('/accounts/register',json={'number':'AE-1234567890123456','recovery':'d'*64,'name':'Test Cadet'}).json()
    auth={'Authorization':'Bearer '+data['token']}
    ids=client.post('/accounts/plan',headers=auth,json={'subject':'powerplant','sourceMode':'IN'}).json()['ids']
    assert len(ids)==50
    payload={'id':'test-private','bankVersion':bank['version'],'subject':'powerplant','answers':[{'id':i,'choice':0} for i in ids]}
    assert client.post('/accounts/results',headers=auth,json=payload).json()['correct']==50
    payload['id']='invalid-choice';payload['answers'][0]['choice']=3
    assert client.post('/accounts/results',headers=auth,json=payload).status_code==422
