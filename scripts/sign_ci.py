"""Use the existing release identity from an encrypted Actions secret."""
import base64
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SECRET = "AE_SIGNING_RECOVERY_ZIP_B64"
LIMIT = 262144


# Recovery input: bounded archive; all private files stay outside the checkout.
def restore_recovery(encoded, directory):
    if len(encoded) > 65536:
        raise ValueError("Recovery secret is too large")
    raw = base64.b64decode("".join(encoded.split()), validate=True)
    directory = Path(directory).resolve()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        if len(entries) > 30 or sum(e.file_size for e in entries) > LIMIT:
            raise ValueError("Recovery archive exceeds limits")
        names = set()
        for entry in entries:
            relative = PurePosixPath(entry.filename)
            if (relative.is_absolute() or ".." in relative.parts
                    or "\\" in entry.filename or ":" in entry.filename
                    or entry.filename in names
                    or stat.S_ISLNK(entry.external_attr >> 16)
                    or entry.flag_bits & 1):
                raise ValueError("Unsafe recovery entry")
            names.add(entry.filename)
            target = directory.joinpath(*relative.parts)
            if not target.resolve().is_relative_to(directory):
                raise ValueError("Recovery entry escapes its directory")
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(entry))
                target.chmod(0o600)
    credentials = list(directory.rglob("signing-recovery.json"))
    if len(credentials) != 1:
        raise ValueError("Expected one recovery credentials file")
    credentials = credentials[0]
    private = json.loads(credentials.read_text())
    for field in ("keystore", "alias", "storePassword", "keyPassword"):
        if not isinstance(private.get(field), str) or not private[field]:
            raise ValueError("Incomplete recovery credentials")
    key = (credentials.parent / private["keystore"]).resolve()
    if not key.is_relative_to(directory) or not key.is_file():
        raise ValueError("Invalid recovery keystore")
    return credentials, private


# Logging: mask decoded secrets before any signing subprocess can run.
def mask(value):
    if os.environ.get("GITHUB_ACTIONS") == "true":
        value = value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        print("::add-mask::" + value, flush=True)


def main():
    encoded = os.environ.pop(SECRET, "")
    # Defense in depth: a dispatch on another branch cannot use the signer.
    if (os.environ.get("GITHUB_REF") != "refs/heads/main"
            or os.environ.get("GITHUB_EVENT_NAME") not in ("push", "workflow_dispatch")):
        print("CI signing is restricted to main pushes or manual runs on main.")
        return 0
    if not encoded:
        print("Signing secret is not configured; signed publication remains blocked.")
        return 0
    config = json.loads((ROOT / "release.json").read_text())
    name = "AE-Prepware-" + config["version"] + "-Signed-Candidate.apk"
    if (ROOT / "release-candidates" / config["version"] / name).exists():
        print("Existing prepared candidate retained for independent verification.")
        return 0
    # TemporaryDirectory removes the key and passwords even if signing fails.
    with tempfile.TemporaryDirectory(prefix="ae-signer-", dir=os.environ["RUNNER_TEMP"]) as folder:
        credentials, private = restore_recovery(encoded, folder)
        for field in ("alias", "storePassword", "keyPassword"):
            mask(private[field])
        command = [sys.executable, str(ROOT / "scripts/sign_release.py"),
                   "--credentials", str(credentials)]
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
        subprocess.run([sys.executable, str(ROOT / "scripts/package_candidate.py"),
                        "--apk", str(ROOT / "artifacts" / name)],
                       cwd=ROOT, check=True, capture_output=True)
    print("Signed candidate prepared with the existing key; packaging verification follows.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        print("CI signing failed. Check the recovery archive and pinned release certificate.", file=sys.stderr)
        raise SystemExit(1)
