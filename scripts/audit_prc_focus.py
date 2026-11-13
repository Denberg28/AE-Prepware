"""Reproducible structural audit and independent spot calculations of the core.

Expected values below are worked separately from generate_bank.py. They cover
all selected numeric exercises; they are not a faculty/content approval gate.
"""
import argparse
import collections
import hashlib
import json
import math
import re
from pathlib import Path

from backend.bank import load_bank

# ID -> independently calculated numeric result in the answer's printed unit.
EXPECTED = {
    'MA001':14,'MA002':9,'MA003':3/5,'MA004':6,'MA005':2,'MA009':12,
    'MA010':5,'MA011':5,'MA013':17,'MA014':6,'MA015':5,'MA016':2,
    'MA017':5,'MA018':8,'MA019':10,'MA028':24,
    'AD001':1500,'AD002':4000,'AD003':4,'AD004':360,'AD008':2,'AD009':2,
    'AD013':960,'AD014':1200,'AD015':.4,'AD016':96,'AD017':.2,'AD018':2,
    'AD019':200,'AD020':40,
    'ST001':100,'ST002':.0005,'ST003':70,'ST004':500,'ST007':10,
    'ST010':2.5,'ST011':.5,'ST013':40,'ST014':.002,'ST015':.2,
    'ST016':1000,'ST017':2000,'ST018':4,'ST019':20,'ST020':2,'ST021':60,
    'CR013':60,'CR014':8,'CR015':5.4,'CR016':500,
    'PP002':2,'PP003':10,'PP007':30,'PP008':10,'PP011':4000,
    'PP013':4.8,'PP014':3,'PP015':20,'PP016':400,'PP017':800,
    'PP018':.2,'PP019':1000,'PP020':80,
    'EE005':2000,'EE006':12100,'EE007':10000,'EE008':20000,'EE009':0,
    'EE010':100,'EE013':200,'EE014':2420,'EE015':2000,'EE016':4000,
    'EE017':200,'EE018':19000,'EE019':2,'EE020':420,
}


def expanded_value(q):
    """Solve the historical parameterized exercise from its printed givens.

    No generator imports, parameter indices, or stored explanations are used.
    Units here match the units in the printed numeric answer.
    """
    v=[float(n.replace(',','')) for n in re.findall(r'[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?',q['prompt'])]
    subject,topic=q['subject'],q['topic']
    if subject=='math':
        return {'Derivatives':lambda:2*v[0]*v[2]+v[1],
                'Integration':lambda:v[0]*v[2]**2/2,
                'Algebra':lambda:v[-4]*v[-1]-v[-3]*v[-2] if 'determinant' in q['prompt'] else (v[2]-v[1])/v[0],
                'Analytic geometry':lambda:(v[3]-v[1])/(v[2]-v[0]),
                'Differential equations':lambda:v[0]*v[3]+v[2],
                'Trigonometry':lambda:math.hypot(*v),
                'Engineering calculus':lambda:2*v[0]*v[1]}[topic]()
    if subject=='aero':
        return {'Dynamic pressure':lambda:v[0]*v[1]**2/2,'Lift':lambda:math.prod(v),
                'Lift coefficient':lambda:v[2]/(v[0]*v[1]),'Drag':lambda:math.prod(v),
                'Compressible flow':lambda:v[0]/v[1],'Wing geometry':lambda:v[0]**2/v[1],
                'Wing loading':lambda:v[0]/v[1],'Continuity':lambda:v[1]*v[3]/v[5]}[topic]()
    if subject=='structures':
        return {'Axial stress':lambda:v[0]/v[1],'Strain':lambda:v[1]/v[0],
                'Elasticity':lambda:v[0]*v[1]/(v[2]*v[3]),'Beam reactions':lambda:v[0]/2,
                'Beam bending':lambda:v[0]*v[1]/4,'Center of gravity':lambda:(v[1]+v[2])/2,
                'Torsion fundamentals':lambda:v[0]*v[1],'Margin of safety':lambda:v[0]/v[1]-1}[topic]()
    if subject=='powerplant':
        return {'Shaft power':lambda:v[0]*v[1]/1000,'Compression ratio':lambda:(v[0]+v[1])/v[1],
                'Thermal efficiency':lambda:100*v[1]/v[0],'Jet thrust':lambda:v[0]*(v[2]-v[1]),
                'Thermodynamic cycles':lambda:v[0]-v[1],'Fuel consumption':lambda:v[1]/v[0],
                'Reciprocating engines':lambda:v[0]/2,'Fuel energy':lambda:v[0]*v[1]}[topic]()
    if subject=='ethics':
        return {'Simple interest':lambda:v[0]/100*v[1]*v[2],
                'Compound interest':lambda:v[0]*(1+v[2]/100)**v[1],
                'Present value':lambda:v[1]/(1+v[0]/100),'Depreciation':lambda:(v[0]-v[1])/v[2],
                'Break-even analysis':lambda:v[0]/(v[1]-v[2]),
                'Cost analysis':lambda:v[0]*(v[1]-v[2])-v[3],
                'Payback':lambda:v[0]/v[1],'Capital budgeting':lambda:v[1]-v[0]}[topic]()
    return {'Repair drawing arithmetic':lambda:(v[0]-1)*v[1],
            'Fastener calculation':lambda:v[1]+v[0]*v[2],
            'Material quantity':lambda:v[0]*v[1]*v[2]/1000*v[3],
            'Joint fundamentals':lambda:v[0]/v[1]}[topic]()


def numeric_answer(q):
    answer=q['choices'][q['answer']]
    match=re.search(r'[-−]?\d[\d,]*(?:\.\d+)?',answer)
    if not match:raise ValueError('No numeric answer: '+q['id'])
    return float(match[0].replace(',','').replace('−','-'))


def audit(path):
    bank=load_bank(path)
    selected=bank['focus']['questions']
    index={q['id']:q for q in bank['questions']}
    checks=[]
    for qid,value in EXPECTED.items():
        if qid not in selected:
            raise ValueError('Numerical audit is out of date: '+qid)
        q=index[qid]; answer=q['choices'][q['answer']]
        if not math.isclose(numeric_answer(q),value,abs_tol=.0005):
            raise ValueError('Independent calculation mismatch: '+qid)
        checks.append({'id':qid,'expected':value,'answer':answer,'result':'matched'})
    expanded=[]
    for q in bank['questions']:
        if q.get('origin','AI')!='AI':continue
        n=int(q['id'][2:])
        if n<13 or (q['subject']=='construction' and n>36):continue
        value=expanded_value(q)
        if not math.isclose(numeric_answer(q),value,abs_tol=.0005):
            raise ValueError('Printed-givens calculation mismatch: '+q['id'])
        expanded.append(q['id'])
    counts={s['id']:{o:sum(index[qid]['subject']==s['id'] and index[qid].get('origin','AI')==o for qid in selected) for o in ('AI','IN')} for s in bank['subjects']}
    areas=[{'id':aid,**area,'coreItems':sum(v['area']==aid for v in selected.values()),
            'status':'foundation-only' if any(v['area']==aid for v in selected.values()) else 'missing'} for aid,area in bank['focus']['areas'].items()]
    normalized=collections.defaultdict(list)
    for q in bank['questions']:
        if q.get('origin','AI')=='AI':
            stem=re.sub(r'\d[\d,.]*','#',q['prompt'].casefold())
            normalized[(q['subject'],stem)].append(q['id'])
    return {'bankVersion':bank['version'],'bankSha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            'records':len(bank['questions']),'coreItems':len(selected),'coreBySubject':counts,
            'coverage':areas,'numericChecks':checks,'numericCheckCount':len(checks),
            'expandedNumericChecks':expanded,'expandedNumericCheckCount':len(expanded),
            'aiRepeatedNumericStemGroups':sum(len(ids)>1 for ids in normalized.values()),
            'auditScope':'All records schema/provenance/duplicate-active validation; all core records selected for relevance; selected AI numeric answers recalculated. IN source-key matching is inherited, not independent faculty review. Nonzero area counts do not demonstrate complete competency coverage.',
            'facultyApproved':False,'authenticPrcPastPapers':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bank',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    report=audit(args.bank);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('bankVersion','records','coreItems','numericCheckCount')}))
