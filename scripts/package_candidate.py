"""Package or verify a permanently signed candidate; never create a debug release.

The signed APK is prepared locally using the private key. CI checks its signature,
Android input digest, exact ZIP payload versus its own unsigned build, and version.
No private signing key is needed in GitHub or committed source.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import ssl
import subprocess
import zipfile
from source_digest import source_digest,ROOT
from apk_contract import payload,vcs_revision

parser=argparse.ArgumentParser()
parser.add_argument('--apk',type=Path)
parser.add_argument('--verify',action='store_true')
args=parser.parse_args()
config=json.loads((ROOT/'release.json').read_text());version=config['version']
sdk=Path(os.environ.get('ANDROID_HOME',os.environ.get('ANDROID_SDK_ROOT','')));tools=sdk/'build-tools/35.0.0'
if not tools.is_dir():raise SystemExit('Set ANDROID_HOME to SDK with build-tools 35.0.0')
name=f'AE-Prepware-{version}-Signed-Candidate.apk'
prepared=ROOT/'release-candidates'/version
package=args.apk or prepared/name
if not package.is_file():raise SystemExit('Signed candidate not prepared. Build release, run sign_release.py, then package_candidate.py --apk /path/to/signed.apk')
if package.stat().st_size>=5_000_000:raise SystemExit('APK exceeds 5 MB')
signature=subprocess.check_output([str(tools/'apksigner'),'verify','--verbose','--print-certs',str(package)],text=True)
match=re.search(r'Signer #1 certificate SHA-256 digest: ([a-f0-9]+)',signature)
if not match or match[1]!=config['certificateSha256']:raise SystemExit('APK signing certificate mismatch')
certificate=ROOT/'signing/AE-Prepware-release-certificate.pem'
if hashlib.sha256(ssl.PEM_cert_to_DER_cert(certificate.read_text())).hexdigest()!=config['certificateSha256']:raise SystemExit('Public certificate mismatch')
manifest=subprocess.check_output([str(tools/'aapt'),'dump','badging',str(package)],text=True)
for expected in ["package: name='ph.diversify.aeprepware'",f"versionName='{version}'",f"versionCode='{config['versionCode']}'","sdkVersion:'26'","targetSdkVersion:'35'"]:
    if expected not in manifest:raise SystemExit('Manifest mismatch: '+expected)
if 'application-debuggable' in manifest:raise SystemExit('Published candidate must not be debuggable')
with zipfile.ZipFile(package) as archive:
    packaged_bank=json.loads(archive.read('assets/bank.json'))
if packaged_bank.get('distribution') == 'private-study' or any(q.get('upload',{}).get('rights') == 'user-provided-private' for q in packaged_bank['questions']):
    raise SystemExit('Private user-supplied guide content must not enter public candidate publication')
# Compare *all* unsigned ZIP payloads except Gradle's source-commit marker, which
# legitimately differs when the prepared artifact is added in a later commit.
unsigned=ROOT/'app/build/outputs/apk/release/app-release-unsigned.apk'
if not unsigned.is_file() or payload(package)!=payload(unsigned):raise SystemExit('Signed APK ZIP payload does not match the rebuilt unsigned release')
sha=hashlib.sha256(package.read_bytes()).hexdigest();digest=source_digest()
source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
if args.verify:
    metadata=json.loads((prepared/'release-manifest.json').read_text())
    if vcs_revision(package)!=metadata['sourceCommit']:raise SystemExit('APK VCS revision does not match recorded source commit')
    if metadata['sha256']!=sha or metadata['androidSourceDigest']!=digest or metadata['certificateSha256']!=config['certificateSha256'] or metadata['version']!=version:raise SystemExit('Prepared artifact metadata mismatch')
    checksums=(prepared/'SHA256SUMS.txt').read_text()
    if checksums!=sha+'  '+name+'\n':raise SystemExit('Checksum file mismatch')
    if metadata['sourceCommit'] not in (prepared/'APK-VERIFICATION.txt').read_text():raise SystemExit('Source identity missing in evidence')
    # Every byte packaged into Android assets must also match the checkout.
    with zipfile.ZipFile(package) as z:
        for p in (ROOT/'app/src/main/assets').iterdir():
            if z.read('assets/'+p.name)!=p.read_bytes():raise SystemExit('Bundled asset mismatch: '+p.name)
    print('PASS signed candidate certificate, manifest, checksum, source digest and rebuilt ZIP payload')
else:
    if vcs_revision(package)!=source:raise SystemExit('Rebuild and sign the current committed source before packaging')
    tracked=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip()
    if tracked:raise SystemExit('Commit source changes before packaging')
    prepared.mkdir(parents=True,exist_ok=True)
    if package.resolve()!=(prepared/name).resolve():shutil.copy2(package,prepared/name)
    bank=json.loads((ROOT/'app/src/main/assets/bank.json').read_text())
    metadata={'version':version,'versionCode':config['versionCode'],'tier':'test-candidate','sourceCommit':source,'androidSourceDigest':digest,'package':'ph.diversify.aeprepware','artifact':name,'bytes':package.stat().st_size,'sha256':sha,'certificateSha256':config['certificateSha256'],'bankVersion':bank['version'],'questions':len(bank['questions']),'androidDeviceTested':False,'facultyApproved':False,'hostedServiceDeployed':False,'liveAiTested':False}
    (prepared/'release-manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (prepared/'APK-VERIFICATION.txt').write_text(f'Candidate: {version}\nSource commit: {source}\nAndroid source digest: {digest}\nSHA256: {sha}\nSigner: permanent AE Prepware release certificate (not debug)\n\n'+signature+'\n'+manifest)
    (prepared/'SHA256SUMS.txt').write_text(sha+'  '+name+'\n')
    shutil.copy2(certificate,prepared/certificate.name)
    print('Prepared '+str(prepared))
