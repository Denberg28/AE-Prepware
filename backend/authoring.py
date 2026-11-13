"""Reviewed, append-only bank edits. Old question IDs always retain their keys."""
import copy
import hashlib
import json
import re
import secrets
from datetime import date

from .bank import validate_bank


def question_content(bank, question):
    """Fields affecting identity, display, and grading; activation may change."""
    return {**{k: question.get(k) for k in (
        'subject', 'topic', 'prompt', 'choices', 'answer', 'explanation', 'source',
        'review', 'reviewer', 'reviewedAt', 'upload', 'supersedes')},
        'origin': question.get('origin', 'AI'),
        'citation': bank['sources'].get(question.get('source'))}


def compatible_refresh(old, new):
    if new.get('extends') != old['version'] or new['version'] == old['version']:
        raise ValueError('Refresh must extend the current bank with a new version')
    index = {q['id']: q for q in new['questions']}
    for q in old['questions']:
        if q['id'] not in index or question_content(old, q) != question_content(new, index[q['id']]):
            raise ValueError('Existing questions and citations must remain unchanged: ' + q['id'])
    validate_bank(new, imported=True, trusted=old)
    if len(json.dumps(new, ensure_ascii=False, indent=2).encode()) > 8_000_000:
        raise ValueError('Bank exceeds the Android 8 MB import limit')
    return new


def revise_question(bank, question_id, *, prompt, choices, answer, explanation, reviewer, version):
    candidate = copy.deepcopy(bank)
    old = next(q for q in candidate['questions'] if q['id'] == question_id)
    if old.get('active', True) is False:
        raise ValueError('Select the active revision')
    if not reviewer.strip():
        raise ValueError('Instructor reviewer name is required')
    updated = {**old, 'id': old['id'][:45] + '-r-' + secrets.token_hex(6),
               'prompt': prompt.strip(), 'choices': [c.strip() for c in choices],
               'answer': answer, 'explanation': explanation.strip(), 'active': True,
               'origin': old.get('origin', 'AI'), 'supersedes': old['id'],
               'review': 'approved', 'reviewer': reviewer.strip(),
               'reviewedAt': date.today().isoformat()}
    old['active'] = False
    candidate['questions'].append(updated)
    candidate.update(version=version.strip(), extends=bank['version'])
    return compatible_refresh(bank, candidate)


def merge_instructor_upload(bank, upload, version):
    """Accept one full six-subject contract, with IN-only questions, atomically."""
    validate_bank(upload, imported=True, partial=True)
    if any(q.get('origin') != 'IN' for q in upload['questions']):
        raise ValueError('Instructor uploads must label every question IN')
    candidate = copy.deepcopy(bank)
    existing = {q['id'] for q in bank['questions']}
    for key, source in upload['sources'].items():
        if key in candidate['sources'] and source != candidate['sources'][key]:
            raise ValueError('Source ID conflicts with an existing citation: ' + key)
        candidate['sources'][key] = source
    for q in upload['questions']:
        if q['id'] in existing:
            raise ValueError('Question ID already exists: ' + q['id'])
        candidate['questions'].append(copy.deepcopy(q))
    candidate.update(version=version.strip(), extends=bank['version'])
    return compatible_refresh(bank, candidate)


def password_hash(password):
    if len(password) < 16:
        raise ValueError('Use at least 16 characters')
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return f'scrypt${salt}${digest}'


def verify_password(password, encoded):
    if len(password) > 1024 or not re.fullmatch(r'scrypt\$[a-f0-9]{32}\$[a-f0-9]{128}', encoded):
        return False
    _, salt, expected = encoded.split('$')
    actual = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
    return secrets.compare_digest(actual, expected)
