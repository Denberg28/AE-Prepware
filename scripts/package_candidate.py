"""Package the already-built, debug-signed candidate with source identity."""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
version='0.1.0-rc.1'
sdk=Path(os.environ.get('ANDROID_HOME',os.environ.get('ANDROID_SDK_ROOT','')))
tools=sdk/'build-tools/35.0.0'
if not tools.is_dir():raise SystemExit('Set ANDROID_HOME to SDK with build-tools 35.0.0')
source=ROOT/'app/build/outputs/apk/debug/app-debug.apk'
if not source.is_file():raise SystemExit('Build :app:assembleDebug first')
output=ROOT/'artifacts';output.mkdir(exist_ok=True)
package=output/f'AE-Prepware-{version}-Test-Candidate.apk'
shutil.copy2(source,package)
assert package.stat().st_size<5_000_000,'APK exceeds 5 MB acceptance limit'
signature=subprocess.check_output([str(tools/'apksigner'),'verify','--verbose','--print-certs',str(package)],text=True)
manifest=subprocess.check_output([str(tools/'aapt'),'dump','badging',str(package)],text=True)
for expected in ["package: name='ph.diversify.aeprepware'", "versionName='0.1.0-rc.1'", "sdkVersion:'26'", "targetSdkVersion:'35'"]:
    assert expected in manifest,expected
sha=hashlib.sha256(package.read_bytes()).hexdigest()
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
# Refuse to misattribute a package when tracked source changes are uncommitted.
if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip():raise SystemExit('Commit tracked source before packaging')
(output/'APK-VERIFICATION.txt').write_text(f'Candidate: {version}\nSource commit: {commit}\nSHA256: {sha}\nSize: {package.stat().st_size} bytes\nSigner: disposable Android debug signer; not production signing\n\n'+signature+'\n'+manifest)
(output/'SHA256SUMS.txt').write_text(sha+'  '+package.name+'\n')
(output/'release-manifest.json').write_text(json.dumps({'version':version,'tier':'test-candidate','commit':commit,'package':'ph.diversify.aeprepware','minSdk':26,'targetSdk':35,'artifact':package.name,'bytes':package.stat().st_size,'sha256':sha,'bankVersion':'2026.11-foundations.1','androidDeviceTested':False,'facultyApproved':False,'hostedServiceDeployed':False,'liveAiTested':False},indent=2)+'\n')
print(package)
