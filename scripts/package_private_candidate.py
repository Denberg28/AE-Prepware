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
sha=hashlib.sha256(output.read_bytes()).hexdigest()
metadata={**config,'artifact':apk_name,'sha256':sha,'bytes':output.stat().st_size,'distribution':'private-study','sourceCommit':source,
          'androidSourceDigest':source_digest(),'bankVersion':bank['version'],'bankSha256':hashlib.sha256(args.bank.read_bytes()).hexdigest(),
          'questions':len(bank['questions']),'aiQuestions':len(bank['questions'])-len(imported),'inQuestions':len(imported),'held':audit['held'],
          'androidDeviceTested':False,'facultyApproved':False,'hostedServiceDeployed':False,'sourceKeyAgreement':True}
(args.output_dir/'private-release-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
(args.output_dir/'APK-VERIFICATION.txt').write_text('Private study candidate. Source: '+source+'\n\n'+signature+'\n'+manifest)
(args.output_dir/'README.txt').write_text(f'''AE Prepware {config["version"]} - private IN study candidate

Install {apk_name} over the permanently signed v0.2/v0.3/v0.4 app, without uninstalling.
Export progress and the current question bank first. Package identity and signer
are unchanged; versionCode {config["versionCode"]}. Physical phone validation is pending.

Includes {len(imported)} IN questions from your two uploaded guides and 360 AI
foundation questions. IN preserves the original A-C choices, source explanations
and printed keys. {audit["held"]} figure/ambiguous questions are held in the review queue.
Subjects: {json.dumps(audit["bySubject"])}

Tick IN or both banks before choosing a subject. IN-only: 50. Hybrid: 25 each.
No Mathematics or Philippine Laws/Ethics IN pool is supplied by these books.
Keys were matched against the PDFs; this is NOT independent faculty approval,
current Philippine regulatory validation, official PRC content or a pass guarantee.

The private bank is persisted in bank storage to survive later app updates. Keep
AE-IN-private-bank.json together with a progress backup before reinstalling or
changing phones. Settings can export both. Use the same private bank in a hosted
API (AE_BANK) for account synchronization; no matching server is deployed here.
Imported book content is private and is not uploaded to the public repository.

Rollback: retain your prior APK and its matching bank/progress backups. Android
blocks lower-version installs; uninstalling deletes local data. Do not uninstall
without those backups. Public APKs do not carry the uploaded guide content.
''')
checks=[]
for p in sorted(args.output_dir.iterdir()):
    if p.is_file() and p.name!='SHA256SUMS.txt' and p.suffix!='.zip':checks.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name)
(args.output_dir/'SHA256SUMS.txt').write_text('\n'.join(checks)+'\n')
print(json.dumps({'artifact':str(output),'sha256':sha,'IN':len(imported),'held':audit['held'],'verified':'certificate, manifest, full unsigned payload, every asset, bank checksum, source commit'}))
