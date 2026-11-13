import json
from pathlib import Path
from backend.bank import load_bank

def test_original_keys_and_wording_preserved():
    baseline=json.loads((Path(__file__).parent/'fixtures/legacy-keys.json').read_text())
    now={q['id']:q for q in load_bank()['questions']}
    assert len(baseline)==72
    for old in baseline:
        assert {k:now[old['id']][k] for k in ('id','prompt','choices','answer')}==old

def test_expanded_arithmetic_examples_and_distinct_stems():
    bank=load_bank();items={q['id']:q for q in bank['questions']}
    assert len({q['prompt'] for q in bank['questions']})==360
    examples={'MA013':'17','MA014':'6','MA015':'5','MA017':'5','MA019':'10 m','AD013':'960 Pa','AD014':'1,200 N','AD015':'0.4','ST013':'40 MPa','ST014':'0.002','ST015':'0.2 mm','ST017':'2,000 N·m','PP013':'4.8 kW','PP014':'3 :1','PP015':'20 %','PP016':'400 N','EE013':'200 pesos','EE014':'2,420 pesos','EE015':'2,000 pesos','CR013':'60 mm','CR014':'8 mm','CR015':'5.4 kg','CR016':'500 N'}
    for qid,expected in examples.items():
        q=items[qid];assert q['choices'][q['answer']]==expected
    assert all(len({c.strip().casefold() for c in q['choices']})==4 for q in bank['questions'])
