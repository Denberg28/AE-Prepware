import base64
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fresh_signer as signer


@pytest.fixture
def fresh_key(tmp_path):
    if not shutil.which("keytool"):
        pytest.fail("JDK keytool is required for signer integration checks")
    directory = tmp_path / "private"
    archive = signer.create(directory)
    return directory, archive


def test_real_key_roundtrip_and_no_overwrite(fresh_key, tmp_path):
    directory, archive = fresh_key
    with pytest.raises(FileExistsError):
        signer.create(directory)
    restored, private = signer.restore_recovery(
        base64.b64encode(archive.read_bytes()).decode(), tmp_path / "restored")
    certificate = signer.keytool(
        ["-exportcert", "-rfc", "-keystore", str(restored.parent / private["keystore"]),
         "-alias", private["alias"]], private["storePassword"])
    assert certificate == (directory / signer.CERTIFICATE).read_bytes()
    assert archive.stat().st_mode & 0o777 == 0o600
    assert restored.stat().st_mode & 0o777 == 0o600
    with zipfile.ZipFile(archive) as contents:
        assert set(contents.namelist()) == {"release.p12", "signing-recovery.json", signer.CERTIFICATE}


def test_activation_failure_preserves_pin_then_success_uses_stdin(fresh_key, tmp_path, monkeypatch):
    _, archive = fresh_key
    repo = tmp_path / "repo"
    (repo / "signing").mkdir(parents=True)
    config = {"version": "test", "certificateSha256": "retired", "signerResetPending": True}
    (repo / "release.json").write_text(json.dumps(config))
    (repo / "signing" / signer.CERTIFICATE).write_bytes(b"retired-public-certificate")
    monkeypatch.setattr(signer, "ROOT", repo)
    real_which, real_run = signer.shutil.which, signer.subprocess.run
    monkeypatch.setattr(signer.shutil, "which", lambda name: "/fixture/gh" if name == "gh" else real_which(name))

    def failed(command, **kwargs):
        if command[0] == "/fixture/gh":
            raise subprocess.CalledProcessError(1, command)
        return real_run(command, **kwargs)

    monkeypatch.setattr(signer.subprocess, "run", failed)
    with pytest.raises(subprocess.CalledProcessError):
        signer.activate(archive)
    assert json.loads((repo / "release.json").read_text()) == config
    assert (repo / "signing" / signer.CERTIFICATE).read_bytes() == b"retired-public-certificate"
    calls = []

    def success(command, **kwargs):
        if command[0] == "/fixture/gh":
            assert command == ["/fixture/gh", "secret", "set", signer.SECRET, "--repo", signer.REPOSITORY]
            assert kwargs["input"] == base64.b64encode(archive.read_bytes()).decode()
            calls.append(True)
            return subprocess.CompletedProcess(command, 0)
        return real_run(command, **kwargs)

    monkeypatch.setattr(signer.subprocess, "run", success)
    digest = signer.activate(archive)
    assert calls == [True]
    active = json.loads((repo / "release.json").read_text())
    assert active["certificateSha256"] == digest
    assert "signerResetPending" not in active
    assert (repo / "signing" / signer.CERTIFICATE).read_bytes() == (archive.parent / signer.CERTIFICATE).read_bytes()


def test_private_material_cannot_enter_checkout():
    with pytest.raises(ValueError):
        signer.create(ROOT / "private-recovery")


def test_pending_reset_blocks_direct_signing_before_private_read(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    script = scripts / "sign_release.py"
    script.write_bytes((ROOT / "scripts/sign_release.py").read_bytes())
    (tmp_path / "release.json").write_text('{"signerResetPending":true}')
    result = subprocess.run(
        [sys.executable, str(script), "--credentials", str(tmp_path / "absent.json")],
        capture_output=True, text=True)
    assert result.returncode != 0
    assert "Activate the fresh signer" in result.stderr


def test_reset_cannot_reactivate_the_retired_certificate(fresh_key, tmp_path, monkeypatch):
    directory, archive = fresh_key
    import hashlib
    import ssl
    digest = hashlib.sha256(ssl.PEM_cert_to_DER_cert(
        (directory / signer.CERTIFICATE).read_text())).hexdigest()
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "release.json").write_text(json.dumps(
        {"certificateSha256": digest, "signerResetPending": True}))
    monkeypatch.setattr(signer, "ROOT", repo)
    with pytest.raises(ValueError, match="retired signer"):
        signer.activate(archive)
