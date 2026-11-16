"""Create a permanent replacement signer locally, then activate its public pin."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import ssl
import subprocess
import tempfile
import zipfile

from sign_ci import restore_recovery

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "Denberg28/AE-Prepware"
SECRET = "AE_SIGNING_RECOVERY_ZIP_B64"
CERTIFICATE = "AE-Prepware-release-certificate.pem"
ARCHIVE = "AE-Prepware-Fresh-Signing-Recovery.zip"


# Private output — Keep the only reusable key outside every repository directory.
def private_path(path):
    path = Path(path).expanduser().resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError("Private signing files must stay outside the repository")
    return path


def keytool(arguments, password):
    executable = shutil.which("keytool")
    if not executable:
        raise ValueError("Install JDK 17+ and put keytool on PATH")
    environment = {**os.environ, "AE_FRESH_STORE_PASSWORD": password}
    return subprocess.run(
        [executable, *arguments, "-storepass:env", "AE_FRESH_STORE_PASSWORD"],
        env=environment, check=True, capture_output=True,
    ).stdout


# Key creation — Generate once; never overwrite an existing recovery directory.
def create(directory):
    directory = private_path(directory)
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    password = secrets.token_urlsafe(32)
    private = {"keystore": "release.p12", "alias": "ae-prepware-fresh",
               "storePassword": password, "keyPassword": password}
    key = directory / private["keystore"]
    keytool(["-genkeypair", "-noprompt", "-keystore", str(key),
             "-storetype", "PKCS12", "-alias", private["alias"],
             "-keyalg", "RSA", "-keysize", "3072", "-sigalg", "SHA256withRSA",
             "-validity", "10950", "-dname", "CN=AE Prepware Release, O=Diversify, C=PH"], password)
    key.chmod(0o600)
    certificate = keytool(["-exportcert", "-rfc", "-keystore", str(key),
                           "-alias", private["alias"]], password)
    (directory / CERTIFICATE).write_bytes(certificate)
    credentials = directory / "signing-recovery.json"
    credentials.write_text(json.dumps(private, indent=2) + "\n", encoding="utf-8")
    credentials.chmod(0o600)
    archive_path = directory / ARCHIVE
    with zipfile.ZipFile(archive_path, "x", zipfile.ZIP_DEFLATED) as archive:
        for path in (key, credentials, directory / CERTIFICATE):
            archive.write(path, path.name)
    archive_path.chmod(0o600)
    return archive_path


# Activation — Validate the real key before sending its recovery ZIP via gh stdin.
# Only the public certificate and digest enter source; no old key is required.
def activate(archive_path):
    archive_path = private_path(archive_path)
    if archive_path.stat().st_size > 49152:
        raise ValueError("Recovery archive exceeds the Actions secret limit")
    encoded = base64.b64encode(archive_path.read_bytes()).decode("ascii")
    with tempfile.TemporaryDirectory(prefix="ae-fresh-validate-") as folder:
        credentials, private = restore_recovery(encoded, folder)
        key = (credentials.parent / private["keystore"]).resolve()
        certificate = keytool(["-exportcert", "-rfc", "-keystore", str(key),
                               "-alias", private["alias"]], private["storePassword"])
        pem = certificate.decode("ascii")
        digest = hashlib.sha256(ssl.PEM_cert_to_DER_cert(pem)).hexdigest()

    config_path = ROOT / "release.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    if config.get("signerResetPending") and digest == config["certificateSha256"]:
        raise ValueError("Reset requires a newly generated certificate, not the retired signer")
    gh = shutil.which("gh")
    if not gh:
        raise ValueError("Install GitHub CLI and run gh auth login")
    subprocess.run([gh, "secret", "set", SECRET, "--repo", REPOSITORY],
                   input=encoded, text=True, check=True, capture_output=True)
    config["certificateSha256"] = digest
    config.pop("signerResetPending", None)
    (ROOT / "signing" / CERTIFICATE).write_bytes(certificate)
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("create", "activate"))
    parser.add_argument("path", type=Path, help="New private directory, or existing recovery ZIP")
    args = parser.parse_args()
    if os.environ.get("GITHUB_ACTIONS") == "true":
        raise ValueError("Run release-key setup locally so the private backup survives")
    if args.action == "create":
        print("Private recovery archive created: " + str(create(args.path)))
        print("Back up this directory privately before activating the signer.")
    else:
        print("New signer configured; public certificate SHA-256: " + activate(args.path))
        print("Commit only release.json and the public certificate, then push to run release checks.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError, zipfile.BadZipFile, KeyError):
        raise SystemExit("Setup failed. Check JDK/GitHub CLI, private paths and recovery files. "
                         "Retain any generated private directory; activation can be retried.")
