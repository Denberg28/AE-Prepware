"""Sign the built release using a private recovery file kept outside the repo."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--credentials',type=Path,required=True)
parser.add_argument('--input',type=Path,default=ROOT/'app/build/outputs/apk/release/app-release-unsigned.apk')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
config=json.loads((ROOT/'release.json').read_text())
private=json.loads(args.credentials.read_text())
key=args.credentials.parent/private['keystore']
sdk=Path(os.environ.get('ANDROID_HOME',os.environ.get('ANDROID_SDK_ROOT','')))
tools=sdk/'build-tools/35.0.0'
if not tools.is_dir():raise SystemExit('Set ANDROID_HOME to an SDK with build-tools 35.0.0')
output=args.output or ROOT/f'artifacts/AE-Prepware-{config["version"]}-Signed-Candidate.apk'
output.parent.mkdir(parents=True,exist_ok=True)
aligned=output.with_suffix('.aligned.apk')
subprocess.run([str(tools/'zipalign'),'-p','-f','4',str(args.input),str(aligned)],check=True,capture_output=True)
env={**os.environ,'AE_SIGN_STORE_PASSWORD':private['storePassword'],'AE_SIGN_KEY_PASSWORD':private['keyPassword']}
try:
    subprocess.run([str(tools/'apksigner'),'sign','--ks',str(key),'--ks-key-alias',private['alias'],'--ks-pass','env:AE_SIGN_STORE_PASSWORD','--key-pass','env:AE_SIGN_KEY_PASSWORD','--v1-signing-enabled','false','--v2-signing-enabled','true','--v3-signing-enabled','true','--v4-signing-enabled','false','--out',str(output),str(aligned)],check=True,env=env,capture_output=True)
finally:
    aligned.unlink(missing_ok=True)
verification=subprocess.check_output([str(tools/'apksigner'),'verify','--verbose','--print-certs',str(output)],text=True)
match=re.search(r'Signer #1 certificate SHA-256 digest: ([a-f0-9]+)',verification)
if not match or match[1]!=config['certificateSha256']:raise SystemExit('Signing certificate does not match the pinned project certificate')
print(f'Signed {output.name}; certificate SHA-256 {match[1]}')
