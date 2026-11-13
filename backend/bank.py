"""Shared question-bank contract: runtime grading never uses AI output."""
import json
from pathlib import Path
SUBJECTS = {'math':10,'aero':25,'structures':20,'construction':15,'powerplant':20,'ethics':10}
BUNDLED = Path(__file__).resolve().parents[1] / 'app/src/main/assets/bank.json'

def validate_bank(bank, imported=False):
    if not isinstance(bank,dict) or bank.get('schema') != 1 or not isinstance(bank.get('version'),str):
        raise ValueError('Unsupported bank version')
    subs=bank.get('subjects',[])
    if len(subs)!=6 or {s['id']:s['weight'] for s in subs} != SUBJECTS:
        raise ValueError('PRC subject weights must match the supported blueprint')
    questions=bank.get('questions',[])
    if not 6<=len(questions)<=3000:
        raise ValueError('Bank requires 6–3000 questions')
    ids=set()
    for q in questions:
        import re
        if not isinstance(q.get('id'),str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',q['id']) or q['id'] in ids:
            raise ValueError('Invalid or duplicate ID')
        ids.add(q['id'])
        if q.get('subject') not in SUBJECTS or not isinstance(q.get('topic'),str) or not q['topic'].strip():
            raise ValueError('Invalid subject/topic')
        choices=q.get('choices',[])
        if len(choices)!=4 or not all(isinstance(c,str) and c.strip() and len(c)<=1000 for c in choices) or len(set(choices))!=4:
            raise ValueError('Exactly four distinct choices are required')
        if type(q.get('answer')) is not int or q['answer'] not in range(4):
            raise ValueError('Invalid answer index')
        for field in ('prompt','explanation'):
            if not isinstance(q.get(field),str) or not 10<=len(q[field])<=4000:
                raise ValueError('Missing prompt/explanation')
        source=bank.get('sources',{}).get(q.get('source'),{})
        if not source.get('title') or not source.get('locator') or not source.get('url','').startswith('https://'):
            raise ValueError('Source title, locator and HTTPS URL are required')
        if q.get('review') not in (('approved',) if imported else ('source-checked','approved')) or not q.get('reviewer') or not q.get('reviewedAt'):
            raise ValueError('Review metadata missing')
    if {q['subject'] for q in questions}!=set(SUBJECTS):
        raise ValueError('Each subject requires at least one question')
    return bank

def load_bank(path=None):
    return validate_bank(json.loads(Path(path or BUNDLED).read_text()), imported=bool(path))
