import base64
import importlib.util
import io
import json
from pathlib import Path
import stat
import zipfile

import pytest

spec = importlib.util.spec_from_file_location("sign_ci", Path(__file__).resolve().parents[1] / "scripts/sign_ci.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


def recovery(extra=(), private=None):
    private = private or {"keystore": "release.jks", "alias": "fixture",
                          "storePassword": "not-a-real-password", "keyPassword": "fixture-password"}
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("private/signing-recovery.json", json.dumps(private))
        archive.writestr("private/release.jks", b"synthetic-keystore")
        for name, data in extra:
            archive.writestr(name, data)
    return base64.b64encode(output.getvalue()).decode()


def test_restore_keeps_valid_fixture_private(tmp_path):
    credentials, private = ci.restore_recovery(recovery(), tmp_path)
    assert credentials.parent == tmp_path / "private"
    assert (credentials.parent / private["keystore"]).read_bytes() == b"synthetic-keystore"
    assert credentials.stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("name", ["../escape", "/absolute", "dir/../../escape", "dir\\escape", "C:/escape"])
def test_rejects_escaping_archive_entries(tmp_path, name):
    with pytest.raises(ValueError):
        ci.restore_recovery(recovery([(name, b"x")]), tmp_path)


def test_rejects_symlink_and_oversized_archives(tmp_path):
    link = zipfile.ZipInfo("link")
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with pytest.raises(ValueError):
        ci.restore_recovery(recovery([(link, "../outside")]), tmp_path)
    with pytest.raises(ValueError):
        ci.restore_recovery(recovery([("large", b"x" * (ci.LIMIT + 1))]), tmp_path)


def test_rejects_keystore_outside_private_directory(tmp_path):
    private = {"keystore": "/etc/passwd", "alias": "fixture",
               "storePassword": "fixture", "keyPassword": "fixture"}
    with pytest.raises(ValueError):
        ci.restore_recovery(recovery(private=private), tmp_path)


def test_no_secret_or_untrusted_event_never_calls_signer(monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.delenv(ci.SECRET, raising=False)
    monkeypatch.setattr(ci.subprocess, "run", lambda *a, **k: pytest.fail("Unexpected signing"))
    assert ci.main() == 0
    assert "publication remains blocked" in capsys.readouterr().out
    monkeypatch.setenv(ci.SECRET, recovery())
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    assert ci.main() == 0
    assert ci.SECRET not in ci.os.environ


def test_success_and_failure_clean_private_files(monkeypatch, tmp_path):
    (tmp_path / "release.json").write_text('{"version":"test"}')
    monkeypatch.setattr(ci, "ROOT", tmp_path)
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "workflow_dispatch")
    monkeypatch.setenv("GITHUB_ACTIONS", "false")
    calls = []

    def run(command, **kwargs):
        assert ci.SECRET not in ci.os.environ
        calls.append(command)
        if "--credentials" in command:
            assert Path(command[-1]).exists()

    monkeypatch.setattr(ci.subprocess, "run", run)
    monkeypatch.setenv(ci.SECRET, recovery())
    assert ci.main() == 0
    assert len(calls) == 2
    assert not list(tmp_path.glob("ae-signer-*"))

    monkeypatch.setenv(ci.SECRET, recovery())
    monkeypatch.setattr(ci.subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("fixture")))
    with pytest.raises(RuntimeError):
        ci.main()
    assert not list(tmp_path.glob("ae-signer-*"))


def test_pending_signer_reset_cannot_use_retired_secret(monkeypatch, tmp_path):
    (tmp_path / "release.json").write_text('{"version":"test","signerResetPending":true}')
    monkeypatch.setattr(ci, "ROOT", tmp_path)
    monkeypatch.setenv("GITHUB_REF", "refs/heads/main")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv(ci.SECRET, recovery())
    monkeypatch.setattr(ci.subprocess, "run", lambda *a, **k: pytest.fail("Retired signer used"))
    with pytest.raises(ValueError, match="Fresh signer activation"):
        ci.main()
