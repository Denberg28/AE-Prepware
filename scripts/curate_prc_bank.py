"""Apply a reviewed selection manifest without deleting or re-keying history.

The manifest selects existing records. It does not generate scored questions.
Private source-key-verified records may be copied into a corrected subject;
the old ID is retired and retained verbatim for queued/history grading.
"""
import argparse
import copy
import json
from pathlib import Path

from backend.authoring import compatible_refresh

ROOT = Path(__file__).resolve().parents[1]


def curate(old, policy, version):
    bank = copy.deepcopy(old)
    index = {q['id']: q for q in bank['questions']}
    focus = copy.deepcopy(policy['focus'])
    focus['questions'] = {}
    for entry in policy['selection']:
        q = index[entry['id']]
        if not q.get('active', True):
            raise ValueError('Cannot select a retired question: ' + q['id'])
        subject = entry.get('subject', q['subject'])
        if subject != q['subject']:
            if q.get('origin') != 'IN' or q['review'] != 'source-key-verified':
                raise ValueError('Subject correction requires private verified source content')
            original = q
            q = {**copy.deepcopy(q), 'id': q['id'] + '-PRC', 'subject': subject,
                 'supersedes': q['id'], 'active': True}
            original['active'] = False
            bank['questions'].append(q)
        focus['questions'][q['id']] = {'area': entry['area']}
    for qid in policy.get('retire', []):
        index[qid]['active'] = False
    bank.update(version=version, extends=old['version'], focus=focus)
    bank['notice'] = policy['notice']
    return compatible_refresh(old, bank)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank', type=Path, required=True)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = curate(json.loads(args.bank.read_text()), json.loads(args.policy.read_text()), args.version)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'version': result['version'], 'retainedRecords': len(result['questions']),
                      'focusQuestions': len(result['focus']['questions'])}))
