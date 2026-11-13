"""Independent solutions from printed givens; no generator formula imports."""
import copy
import json
import math
import re
from pathlib import Path

from backend.bank import load_bank, validate_bank
from backend.authoring import question_content


def test_feedback_answers_from_printed_givens_and_provenance():
    bank=load_bank();pack=[q for q in bank['questions'] if q['id'].startswith('FB-')]
    assert len(pack)==20
    for q in pack:
        nums=[float(n) for n in re.findall(r'\d+(?:\.\d+)?',q['prompt'])]
        code=q['id'];actual=float(re.search(r'[0-9.]+',q['choices'][q['answer']])[0])
        if code.startswith('FB-B'):
            expected=(nums[0]+(nums[1] if int(code[-2:])<=3 else 180))%360
        elif code in ('FB-H01','FB-H02','FB-H03'):
            matches=re.findall(r'(\d+)° ([EW])',q['prompt'])
            expected=(nums[0]-sum(float(x)*(1 if d=='E' else -1) for x,d in matches))%360
        elif code.startswith('FB-H'):
            # Independent wind vector: east/right air component cancels the crosswind.
            along=math.sqrt(nums[1]**2-nums[2]**2)
            expected=(nums[0]+math.degrees(math.atan2(-nums[2],along)))%360
        elif code in ('FB-T01','FB-T02'):
            expected=nums[0]/nums[1]/nums[2]
        elif code in ('FB-T03','FB-T04'):
            g,gas,p0,t0,mass=nums[:5]
            # Compute sonic static properties, then use local rho*a continuity.
            temp=t0*2/(g+1);pressure=p0*1000*(temp/t0)**(g/(g-1))
            density=pressure/(gas*temp);speed=math.sqrt(g*gas*temp)
            expected=mass/(density*speed)*10000
        elif code in ('FB-T05','FB-T06'):
            g,mach,area=nums[:3]
            temp_ratio=1/(1+(g-1)*mach**2/2)
            rho_ratio=temp_ratio**(1/(g-1))
            star_temp=2/(g+1);star_rho=star_temp**(1/(g-1))
            ratio=star_rho*math.sqrt(star_temp)/(rho_ratio*mach*math.sqrt(temp_ratio))
            expected=area/ratio*10000
        else:
            g,p0,t0=nums[:3];expected=t0/(1+(g-1)/2) if code=='FB-T07' else p0/(1+(g-1)/2)**(g/(g-1))
        assert math.isclose(actual,expected,abs_tol=.0005), (code,actual,expected)
        assert len(set(q['choices']))==4 and q['origin']=='AI' and q['review']=='source-checked'
        assert 'faculty review pending' in q['reviewer'] and bank['sources'][q['source']]['url'].startswith('https://')


def test_append_only_pack_does_not_change_previous_questions_or_small_core():
    from scripts.add_feedback_practice import extend
    bank=load_bank();old=copy.deepcopy(bank)
    old['questions']=[q for q in old['questions'] if not q['id'].startswith('FB-')]
    old['sources']={k:v for k,v in old['sources'].items() if not k.startswith('feedback-')}
    old['version']=bank['extends'].removesuffix('-feedback1');old.pop('extends',None)
    old['focus']['questions']={k:v for k,v in old['focus']['questions'].items() if not k.startswith('FB-')}
    generated=extend(old)
    assert generated['questions']==bank['questions']
    assert all(q['id'] in bank['focus']['questions'] for q in bank['questions'] if q['id'].startswith('FB-'))
    assert len(bank['focus']['questions'])==140
    index={q['id']:q for q in bank['questions']}
    for q in old['questions']:assert question_content(old,q)==question_content(bank,index[q['id']])
    validate_bank(bank)
