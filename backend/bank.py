"""Shared question-bank contract: runtime grading never uses AI output."""
import json
from pathlib import Path
SUBJECTS = {'math':10,'aero':25,'structures':20,'construction':15,'powerplant':20,'ethics':10}
BUNDLED = Path(__file__).resolve().parents[1] / 'app/src/main/assets/bank.json'

def validate_bank(bank, imported=False, trusted=None, partial=False):
    if not isinstance(bank,dict) or bank.get('schema') != 1 or not isinstance(bank.get('version'),str) or not 1<=len(bank['version'].strip())<=100 or not isinstance(bank.get('blueprintSource'),str) or not bank['blueprintSource'].startswith('https://'):
        raise ValueError('Unsupported bank version')
    subs=bank.get('subjects',[])
    if len(subs)!=6 or {s['id']:s['weight'] for s in subs} != SUBJECTS:
        raise ValueError('PRC subject weights must match the supported blueprint')
    questions=bank.get('questions',[])
    if not (1 if partial else 6)<=len(questions)<=3000:
        raise ValueError('Bank requires 6–3000 questions (1–3000 for instructor uploads)')
    ids=set()
    active_content=set()
    trusted_questions = {q['id']: q for q in trusted['questions']} if trusted else {}
    for q in questions:
        import re
        if not isinstance(q.get('id'),str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',q['id']) or q['id'] in ids:
            raise ValueError('Invalid or duplicate ID')
        ids.add(q['id'])
        if q.get('subject') not in SUBJECTS or not isinstance(q.get('topic'),str) or not q['topic'].strip() or len(q['topic'])>200:
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
        if q.get('origin', 'AI') not in ('AI', 'IN') or ('active' in q and type(q['active']) is not bool):
            raise ValueError('Invalid AI/IN origin or activation state')
        fingerprint = (q['prompt'].strip().casefold(), tuple(sorted(c.strip().casefold() for c in choices)))
        if q.get('active', True):
            if fingerprint in active_content:
                raise ValueError('Duplicate active question content')
            active_content.add(fingerprint)
        if q.get('origin') == 'IN':
            upload = q.get('upload', {})
            if not isinstance(upload, dict) or not all(isinstance(upload.get(k), str) and upload[k].strip() and len(upload[k])<=500 for k in ('file', 'locator', 'rights')) or upload['rights'] not in ('instructor-original', 'permission-granted', 'public-domain', 'open-license') or q.get('review') != 'approved':
                raise ValueError('IN questions require instructor approval and upload provenance/rights')
        unchanged = False
        if q['id'] in trusted_questions:
            from .authoring import question_content
            unchanged = question_content(bank, q) == question_content(trusted, trusted_questions[q['id']])
        if q.get('review') not in (('approved',) if imported and not unchanged else ('source-checked','approved')) or not q.get('reviewer') or not q.get('reviewedAt'):
            raise ValueError('Review metadata missing')
        if not isinstance(q['reviewer'], str) or not q['reviewer'].strip() or len(q['reviewer'])>200 or not isinstance(q['reviewedAt'], str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', q['reviewedAt']):
            raise ValueError('Invalid review metadata')
    if not partial and {q['subject'] for q in questions}!=set(SUBJECTS):
        raise ValueError('Each subject requires at least one question')
    return bank

def load_bank(path=None):
    bundled = json.loads(BUNDLED.read_text())
    return validate_bank(json.loads(Path(path).read_text()), imported=True, trusted=bundled) if path else validate_bank(bundled)
