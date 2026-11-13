"""Extract user-supplied ASA-style guides for private study, never public git.

Requires PyMuPDF in the authoring environment only. Typography separates original
italic explanations from A-C choices. Answer keys must match printed footers.
Ambiguous, duplicate, and figure-dependent records are held in a review queue.
No AI-generated options, keys, explanations or faculty approvals are added.
"""
import argparse
import copy
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
QID = re.compile(r'^([89]\d{3}(?:-\d+)?)\.\s*(.*)')
KEY = re.compile(r'\b([89]\d{3}(?:-\d+)?)\s*\[([ABCX])\]')
OPTION = re.compile(r'^([ABC])\s*[—–-]\s*(.*)')
FIGURE = re.compile(r'\b(?:figure|illustration|diagram|chart)\b|\bshown\s+(?:below|above|in)\b', re.I)
SUPER = str.maketrans('0123456789+-=()n', '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ')
AERO_TOPICS = {'Assembly and Rigging'}
STRUCTURE_TOPICS = {'Wood Structures', 'Sheet Metal and Non-Metallic Structures'}


def normalize(lines, words):
    value = '\n'.join(lines).replace('\u00ad\n', '').replace('\u00ad', '')
    def join(match):
        first, second = match.group(1), match.group(2)
        return first + second if (first + second).lower() in words else first + '-' + second
    value = re.sub(r'([A-Za-z]+)-\n([a-z]+)', join, value)
    return re.sub(r'\s+', ' ', value).strip()


def page_lines(page):
    records = []
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            spans = line['spans']
            text = ''.join(s['text'].translate(SUPER) if s['flags'] & 1 else s['text'] for s in spans)
            if text.strip():
                records.append({'text': text.strip(), 'x': line['bbox'][0], 'y': line['bbox'][1],
                    'italic': any(('Oblique' in s['font'] or 'Italic' in s['font']) and s['text'].strip() for s in spans),
                    'size': max(s['size'] for s in spans)})
    return records


def extract(path, book):
    document = fitz.open(path)
    all_text = '\n'.join(p.get_text() for p in document)
    words = {w.lower() for w in re.findall(r'\b[A-Za-z]{3,}\b', all_text)}
    keys = defaultdict(list)
    items = []
    current = None
    topic = ''
    started = False
    for page_index, page in enumerate(document):
        lines = page_lines(page)
        has_questions = any(QID.match(line['text']) and line['y'] > 49 for line in lines)
        if not started and not has_questions:
            continue
        if not has_questions and re.search(r'Oral\s*(?:&|and)\s*Practical', page.get_text()):
            break
        started = True
        for number, key in KEY.findall(page.get_text()):
            keys[number].append({'key': key, 'pdfPage': page_index + 1})
        footer = min((line['y'] for line in lines if line['y'] > 600 and line['text'].startswith('Answers')), default=page.rect.height-58)
        headings = [line['text'] for line in lines if line['size'] >= 14 and 49 <= line['y'] < footer]
        if headings:
            topic = ' '.join(headings)
        body = [line for line in lines if 49 <= line['y'] < footer and line['size'] < 14]
        # Odd/even book pages have mirrored inner margins. Derive the
        # gutter from this page's left text margin, not the PDF midpoint.
        left_margin = min((line['x'] for line in body if 10 < line['x'] < 100), default=63)
        gutter = left_margin + 259
        for column in (0, 1):
            column_lines = sorted((line for line in body if (line['x'] >= gutter) == bool(column)), key=lambda x: (round(x['y'], 1), x['x']))
            for line in column_lines:
                text = line['text']
                match = QID.match(text)
                if match:
                    if current:
                        items.append(current)
                    current = {'number': match[1], 'topic': topic, 'pdfPage': page_index+1,
                        'promptLines': [match[2]], 'options': {}, 'explanationLines': [], 'part': 'prompt'}
                    continue
                if current is None:
                    continue
                option = OPTION.match(text)
                if option and current['part'] != 'explanation':
                    letter = option[1]
                    if letter in current['options']:
                        current['ambiguous'] = True
                    current['options'][letter] = [option[2]]
                    current['part'] = letter
                elif line['italic'] and 'C' in current['options']:
                    current['part'] = 'explanation'
                    current['explanationLines'].append(text)
                elif current['part'] == 'explanation':
                    current['explanationLines'].append(text)
                elif current['part'] in 'ABC' and current['part'] != 'prompt':
                    current['options'][current['part']].append(text)
                else:
                    current['promptLines'].append(text)
    if current:
        items.append(current)
    counts = Counter(item['number'] for item in items)
    accepted, held = [], []
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    seen_content = set()
    for item in items:
        prompt = normalize(item['promptLines'], words)
        choices = [normalize(item['options'][letter], words) for letter in 'ABC' if letter in item['options']]
        explanation = normalize(item['explanationLines'], words)
        candidates = keys.get(item['number'], [])
        letters = {k['key'] for k in candidates}
        reasons = []
        if counts[item['number']] != 1: reasons.append('duplicate-source-number')
        if item.get('ambiguous') or list(item['options']) != list('ABC'): reasons.append('ambiguous-choice-boundary')
        if len(letters) != 1 or not letters <= set('ABC'): reasons.append('missing-conflicting-or-X-answer-key')
        if len(choices) != 3 or len(set(c.casefold() for c in choices)) != 3: reasons.append('incomplete-or-duplicate-options')
        if not 10 <= len(prompt) <= 4000 or not 10 <= len(explanation) <= 4000 or any(not c or len(c)>1000 for c in choices): reasons.append('incomplete-or-overlong-text')
        if FIGURE.search(prompt + ' ' + ' '.join(choices) + ' ' + explanation): reasons.append('figure-or-chart-dependent')
        if '\ufffd' in prompt + explanation + ''.join(choices): reasons.append('unrecognized-source-glyph')
        fingerprint = (prompt.casefold(), tuple(sorted(c.casefold() for c in choices)))
        if fingerprint in seen_content: reasons.append('duplicate-question-content')
        record = {'book': book, 'number': item['number'], 'pdfPage': item['pdfPage'], 'topic': item['topic'],
                  'prompt': prompt, 'choices': choices, 'explanation': explanation, 'keyEvidence': candidates}
        if reasons:
            held.append({**record, 'reasons': reasons})
            continue
        seen_content.add(fingerprint)
        key = next(iter(letters))
        subject = 'powerplant' if book == 'powerplant' else 'aero' if item['topic'] in AERO_TOPICS else 'structures' if item['topic'] in STRUCTURE_TOPICS else 'construction'
        accepted.append({'id': f'IN-{"AF" if book == "airframe" else "PP"}-{item["number"]}', 'origin': 'IN', 'subject': subject,
            'topic': item['topic'], 'prompt': prompt, 'choices': choices, 'answer': 'ABC'.index(key),
            'explanation': explanation, 'source': 'private-'+book,
            'review': 'source-key-verified', 'reviewer': 'PDF extraction / printed answer-key match; faculty review pending',
            'reviewedAt': date.today().isoformat(),
            'upload': {'file': path.name, 'locator': f'PDF page {item["pdfPage"]}; question {item["number"]}; printed key [{key}]',
                'rights': 'user-provided-private', 'sha256': digest, 'key': key,
                'keyPage': candidates[0]['pdfPage'], 'mapping': 'chapter-based; faculty TOS review pending'}})
    return accepted, held, {'file': path.name, 'sha256': digest, 'pages': len(document), 'sourceQuestions': len(items), 'imported': len(accepted), 'held': len(held)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--airframe', type=Path, required=True)
    parser.add_argument('--powerplant', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    bank = json.loads((ROOT/'app/src/main/assets/bank.json').read_text())
    bank.update(version='2026.11-private-guides.1', extends=bank['version'], distribution='private-study',
        notice='Private study copy: uploaded 2018/2019 FAA-oriented guides. IN keys match the printed source, not independent faculty approval or current Philippine rules. Figure/ambiguous items are held out. No official PRC affiliation or pass guarantee.')
    all_held, reports = [], []
    for book, path in [('airframe', args.airframe), ('powerplant', args.powerplant)]:
        items, held, report = extract(path, book)
        bank['questions'].extend(items)
        bank['sources']['private-'+book] = {'title': ('2019 Airframe' if book == 'airframe' else '2018 Powerplant')+' Test Guide — user-supplied private study copy',
            'url': 'https://asa2fly.com/', 'locator': 'Individual PDF page, source question and printed answer key appear with each IN item. Historical FAA study material; faculty mapping/current-rule review pending.'}
        all_held.extend(held); reports.append(report)
    report = {'distribution': 'private-study', 'books': reports, 'imported': sum(r['imported'] for r in reports),
        'held': len(all_held), 'bySubject': dict(Counter(q['subject'] for q in bank['questions'] if q.get('origin') == 'IN')),
        'reasonCounts': dict(Counter(reason for q in all_held for reason in q['reasons'])),
        'review': 'Source/footer key agreement and structural checks only. Independent faculty review pending.'}
    (args.output_dir/'AE-IN-private-bank.json').write_text(json.dumps(bank, ensure_ascii=False, separators=(',', ':'))+'\n')
    (args.output_dir/'AE-IN-import-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    (args.output_dir/'AE-IN-review-queue.json').write_text(json.dumps(all_held, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
