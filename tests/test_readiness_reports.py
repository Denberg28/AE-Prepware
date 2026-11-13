import copy
import json
from pathlib import Path
import pytest
from backend.readiness_reports import analyze_report, cohort_rows, export_csv, DAY

FIXTURE=Path(__file__).parent/'fixtures/readiness-report.json'

def analyze(data):
    return analyze_report(json.dumps(data).encode(),now=data['generatedAt'])

def test_real_js_export_and_faculty_calculations_agree():
    data=json.loads(FIXTURE.read_text());r=analyze(data)
    assert r['Subjects checked']==data['competence']['assessed']==6
    assert r['Weighted foundation %']==data['competence']['weighted']==88
    assert r['Subject support']=='aero' and r['Board readiness']=='Not established'
    assert [x['status'] for x in r['subjects']]==[x['status'] for x in data['competence']['subjects']]
    assert r['Observed days / 7']==1 and r['Active days / 7']==1
    data['readiness']['status']='Guaranteed pass';data['competence']['weighted']=100
    assert analyze(data)['Weighted foundation %']==88

def test_faculty_reports_deduplicate_latest_profile_and_escape_csv_formulas():
    data=json.loads(FIXTURE.read_text());old=analyze(data);data['alias']='=1+2';data['generatedAt']+=1000;new=analyze(data)
    rows=cohort_rows([new,old]);assert len(rows)==1 and rows[0]['Alias']=='=1+2'
    assert "'=1+2" in export_csv(rows)
    assert 'profile' not in rows[0] and 'subjects' not in rows[0]

def test_invalid_or_incomparable_evidence_is_rejected():
    data=json.loads(FIXTURE.read_text())
    changes=[lambda b:b.update(schema=2),lambda b:b.update(commitment=None),lambda b:b.update(competence=[]),
             lambda b:b['commitment']['goal'].update(days=True),lambda b:b['commitment']['days'][0].update(questions=-1),
             lambda b:b['commitment']['days'][0].update(date='2026-02-31'),lambda b:b['competence']['subjects'][0].update(weight=99),
             lambda b:b['competence']['subjects'][0]['checks'].append(b['competence']['subjects'][0]['checks'][0]),
             lambda b:b['competence']['subjects'][0]['checks'][0].update(correct=21)]
    for change in changes:
        bad=copy.deepcopy(data);change(bad)
        with pytest.raises(ValueError):analyze(bad)
    with pytest.raises(ValueError):analyze_report(b'['*10000)
    with pytest.raises(ValueError):analyze_report(b' '*200001)

def test_stale_and_unobserved_windows_do_not_become_low_commitment_labels():
    data=json.loads(FIXTURE.read_text());r=analyze_report(json.dumps(data).encode(),now=data['generatedAt']+40*DAY)
    assert r['Report age (days)']==40 and r['Subjects checked']==0 and r['Weighted foundation %'] is None
    data['trackingSince']=None;data['commitment']['days']=[{**d,'questions':0} for d in data['commitment']['days']]
    r=analyze(data);assert r['Observed days / 7']==0 and r['Active days / 7'] is None
