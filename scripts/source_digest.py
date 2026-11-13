"""Digest Android inputs independently of git metadata and prepared APK files."""
import hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def source_digest():
    files=list((ROOT/'app/src').rglob('*'))+list((ROOT/'gradle/wrapper').glob('*'))+[
        ROOT/p for p in ('app/build.gradle','build.gradle','settings.gradle','gradle.properties','release.json','signing/AE-Prepware-release-certificate.pem')]
    digest=hashlib.sha256()
    for p in sorted(p for p in files if p.is_file()):
        digest.update(p.relative_to(ROOT).as_posix().encode()+b'\0'+hashlib.sha256(p.read_bytes()).digest())
    return digest.hexdigest()

if __name__=='__main__':print(source_digest())
