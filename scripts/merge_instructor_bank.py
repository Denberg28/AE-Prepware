"""Validate reviewed IN JSON files and export one append-only Android/API refresh."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.authoring import compatible_refresh, merge_instructor_upload
from backend.bank import load_bank
parser = argparse.ArgumentParser()
parser.add_argument('files', nargs='+', type=Path)
parser.add_argument('--base', type=Path)
parser.add_argument('--version', required=True)
parser.add_argument('--output', required=True, type=Path)
args = parser.parse_args()
base = load_bank(args.base)
merged = base
for i, path in enumerate(args.files):
    if path.stat().st_size > 2_000_000:
        raise SystemExit('Upload exceeds 2 MB: ' + path.name)
    merged = merge_instructor_upload(merged, json.loads(path.read_text()), args.version + '-part' + str(i+1))
merged.update(version=args.version, extends=base['version'])
compatible_refresh(base, merged)
encoded = json.dumps(merged, ensure_ascii=False, indent=2) + '\n'
if len(encoded.encode()) > 2_000_000:
    raise SystemExit('Merged bank exceeds the Android 2 MB import limit')
if args.output.exists():
    raise SystemExit('Output already exists; choose a new filename')
args.output.write_text(encoded)
print(f'Exported {len(merged["questions"])-len(base["questions"])} reviewed IN questions to {args.output}')
