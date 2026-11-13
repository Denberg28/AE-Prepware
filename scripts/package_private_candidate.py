"""Verify and package a private IN build; never write into release-candidates."""
import argparse
import hashlib
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.bank import load_bank
from apk_contract import payload, vcs_revision
from source_digest import ROOT, source_digest

parser=argparse.ArgumentParser()
parser.add_argument('--apk',type=Path,required=True)
parser.add_argument('--unsigned',type=Path,required=True)
parser.add_argument('--bank',type=Path,required=True)
parser.add_argument('--audit',type=Path,required=True)
parser.add_argument('--queue',type=Path,required=True)
parser.add_argument('--focus-audit',type=Path)
parser.add_argument('--focus-policy',type=Path)
parser.add_argument('--output-dir',type=Path,required=True)
args=parser.parse_args()
if 'release-candidates' in args.output_dir.resolve().parts:
    raise SystemExit('Private content cannot be packaged for public release')
config=json.loads((ROOT/'release.json').read_text())
bank=load_bank(args.bank)
if bank.get('distribution')!='private-study':raise SystemExit('A private-study bank is required')
sdk=Path(os.environ.get('ANDROID_HOME',os.environ.get('ANDROID_SDK_ROOT','')));tools=sdk/'build-tools/35.0.0'
signature=subprocess.check_output([str(tools/'apksigner'),'verify','--verbose','--print-certs',str(args.apk)],text=True)
match=re.search(r'Signer #1 certificate SHA-256 digest: ([a-f0-9]+)',signature)
if not match or match[1]!=config['certificateSha256']:raise SystemExit('Private candidate signing identity mismatch')
manifest=subprocess.check_output([str(tools/'aapt'),'dump','badging',str(args.apk)],text=True)
for expected in ["package: name='ph.diversify.aeprepware'",f"versionName='{config['version']}'",f"versionCode='{config['versionCode']}'","sdkVersion:'26'","targetSdkVersion:'35'"]:
    if expected not in manifest:raise SystemExit('Manifest mismatch: '+expected)
if 'application-debuggable' in manifest:raise SystemExit('Private candidate must be non-debuggable')
if payload(args.apk)!=payload(args.unsigned):raise SystemExit('Private signed/unsigned payload mismatch')
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
if vcs_revision(args.apk)!=source:raise SystemExit('Private APK source commit mismatch')
with zipfile.ZipFile(args.apk) as archive:
    expected={p.name:(args.bank.read_bytes() if p.name=='bank.json' else p.read_bytes()) for p in (ROOT/'app/src/main/assets').iterdir() if p.is_file()}
    actual={p.removeprefix('assets/') for p in archive.namelist() if p.startswith('assets/') and not p.endswith('/')}
    if actual!=set(expected):raise SystemExit('Private asset inventory mismatch')
    for name,data in expected.items():
        if archive.read('assets/'+name)!=data:raise SystemExit('Private asset mismatch: '+name)
audit=json.loads(args.audit.read_text())
imported=[q for q in bank['questions'] if q.get('origin')=='IN']
if audit['imported']!=len(imported):raise SystemExit('Import count mismatch')
args.output_dir.mkdir(parents=True,exist_ok=True)
apk_name=f'AE-Prepware-{config["version"]}-IN-Private.apk'
output=args.output_dir/apk_name
shutil.copy2(args.apk,output)
for p in [args.bank,args.audit,args.queue]:shutil.copy2(p,args.output_dir/p.name)
if bank.get('focus'):
    if not args.focus_audit or not args.focus_policy:raise SystemExit('Focused candidates require their audit and selection policy')
    focus_audit=json.loads(args.focus_audit.read_text())
    if focus_audit['bankSha256']!=hashlib.sha256(args.bank.read_bytes()).hexdigest() or focus_audit['coreItems']!=len(bank['focus']['questions']):raise SystemExit('Focus audit does not match the candidate bank')
    for p in [args.focus_audit,args.focus_policy,ROOT/'docs/PRC_2022_2026_REVIEW.md',ROOT/'docs/prc-research-sources.json',ROOT/'docs/BOARD_READINESS.md',ROOT/'docs/ONLINE_SYNC.md']:shutil.copy2(p,args.output_dir/p.name)
sha=hashlib.sha256(output.read_bytes()).hexdigest()
metadata={**config,'artifact':apk_name,'sha256':sha,'bytes':output.stat().st_size,'distribution':'private-study','sourceCommit':source,
          'androidSourceDigest':source_digest(),'bankVersion':bank['version'],'bankSha256':hashlib.sha256(args.bank.read_bytes()).hexdigest(),
          'questions':len(bank['questions']),'aiQuestions':len(bank['questions'])-len(imported),'inQuestions':len(imported),'held':audit['held'],
          'androidDeviceTested':False,'facultyApproved':False,'hostedServiceDeployed':False,'sourceKeyAgreement':True,
          'coreQuestions':len(bank.get('focus',{}).get('questions',{})),
          'uniqueInSourceQuestions':audit.get('uniqueSourceQuestions',len(imported)),
          'subjectCorrectionCopies':audit.get('subjectCorrectionCopies',0),
          'retiredForReview':len(audit.get('additionalRetiredReview',[]))}
(args.output_dir/'private-release-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
(args.output_dir/'APK-VERIFICATION.txt').write_text('Private study candidate. Source: '+source+'\n\n'+signature+'\n'+manifest)
(args.output_dir/'README.txt').write_text(f'''AE Prepware {config["version"]} - private IN study candidate

Install {apk_name} over the permanently signed prior candidate, without uninstalling.
Export progress and the current question bank first. Package identity and signer
are unchanged; versionCode {config["versionCode"]}. Physical phone validation is pending.

The default PRC foundations set contains {len(bank.get('focus',{}).get('questions',{}))} selected items.
The full snapshot retains 380 AI records and {audit.get('uniqueSourceQuestions',len(imported))} unique
IN source records, plus {audit.get('subjectCorrectionCopies',0)} copies with corrected subject assignments.
Old IDs, original A-C choices, source explanations and printed keys are preserved.
{audit["held"]} original figure/ambiguous imports remain held; {len(audit.get('additionalRetiredReview',[]))}
additional imported records were retired for content/wording review. ST005 is
retired because its stem depends on a preceding question. No historical key changed.

Core drills: 20 from one source, or 10 AI + 10 IN. Full bank: 50, or 25 each.
Insufficient source pools are disabled; Full bank may have additional material.
No Mathematics or Philippine Laws/Ethics IN pool is supplied by these books.
Keys were matched against the PDFs; this is NOT independent faculty approval,
current Philippine regulatory validation, official PRC content or a pass guarantee.

The immediately preceding private bank auto-refreshes after compatibility and
saved-progress validation. Other/custom versions are preserved; import this JSON
in Settings if an automatic compatible refresh is not offered. The private bank
is persisted in bank storage to survive later app updates. Keep
AE-IN-private-bank.json together with a progress backup before reinstalling or
changing phones. Settings can export both. Use the same private bank in a hosted
API (AE_BANK) for account synchronization; no matching server is deployed here.
Imported book content is private and is not uploaded to the public repository.

Board Readiness Monitoring is under Results. New-item diagnostics and seven-day
spaced checks reveal feedback after submission. Participation is not motivation;
foundation targets do not certify board readiness. Voluntary facilitator JSON
reports can be opened in the private faculty dashboard. Monitoring works offline and is included in progress backups. Full Sync also
backs up the journal and unfinished check to the configured persistent service;
ranking and facilitator sharing are separate opt-ins.
Read BOARD_READINESS.md for rules, limitations and facilitator instructions.

Rollback: retain your prior APK and its matching bank/progress backups. Android
blocks lower-version installs; uninstalling deletes local data. Do not uninstall
without those backups. Public APKs do not carry the uploaded guide content.
''')
checks=[]
for p in sorted(args.output_dir.iterdir()):
    if p.is_file() and p.name!='SHA256SUMS.txt' and p.suffix!='.zip':checks.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name)
(args.output_dir/'SHA256SUMS.txt').write_text('\n'.join(checks)+'\n')
print(json.dumps({'artifact':str(output),'sha256':sha,'IN':len(imported),'held':audit['held'],'verified':'certificate, manifest, full unsigned payload, every asset, bank checksum, source commit'}))
