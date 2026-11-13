"""Exact unsigned APK payload and strictly validated AGP source metadata."""
import re
import zipfile

VCS_ENTRY='META-INF/version-control-info.textproto'
VCS_PATTERN=re.compile(r'repositories\s*\{\s*system:\s*GIT\s*local_root_path:\s*"\$PROJECT_DIR"\s*revision:\s*"([a-f0-9]{40})"\s*\}\s*')

def vcs_revision(path):
    with zipfile.ZipFile(path) as z:
        match=VCS_PATTERN.fullmatch(z.read(VCS_ENTRY).decode('utf-8'))
    if not match:
        raise ValueError('Unexpected AGP version-control metadata')
    return match[1]

def payload(path):
    # The source revision differs when a later commit adds the prepared APK.
    # Its format/revision is checked separately; executable/resource bytes never vary.
    vcs_revision(path)
    with zipfile.ZipFile(path) as z:
        return {n:z.read(n) for n in z.namelist() if not n.endswith('/') and n!=VCS_ENTRY}
