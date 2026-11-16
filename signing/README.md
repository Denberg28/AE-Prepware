# Permanent APK signer — v0.2 onward

The public certificate in this directory pins the AE Prepware update identity. Its SHA-256 digest is in `release.json`. Package name stays `ph.diversify.aeprepware`. v0.2.0-rc.1 has versionCode 2; future updates must raise versionCode and use the same private key/certificate.

The user explicitly authorized permanent signing on 2026-11-13. Private key and password are in the private **AE-Prepware-Private-Signing-Recovery.zip** recovery archive, not this public repository. Keep that archive private and backed up offline. The public certificate alone cannot sign updates.

Restore recovery files to a private directory outside the repository, then:

```sh
./gradlew :app:assembleDebug :app:assembleRelease :app:lint
python scripts/sign_release.py --credentials /private/path/signing-recovery.json
# Commit final source before packaging; the source tree must be clean.
python scripts/package_candidate.py --apk artifacts/AE-Prepware-0.8.3-rc.1-Signed-Candidate.apk
python scripts/package_candidate.py --verify
```

The APK filename must match the current `release.json` version; the command above targets v0.8.3-rc.1. See [current release status](../docs/STATUS.md) for observed signing/publication evidence. A request to build a signed release uses this permanent identity; generating a replacement key requires a separate migration decision because it changes update compatibility.

Set `ANDROID_HOME` to the SDK with build-tools 35.0.0. Signing reads passwords from private file into process environment; values are not printed or embedded in the APK. Do not pass passwords on the command line, commit recovery files, or upload them to GitHub Releases.

Prepared signed APKs and public verification metadata under `release-candidates/<version>/` are public. CI runs all tests, builds the unsigned release, verifies the permanent certificate, source digest, exact unsigned ZIP payload (apart from Gradle's VCS marker), version, checksum and packaged assets. Only then does it publish the same signed candidate. Keeping prepared signed binaries in source makes this small project releaseable without sending the private key to CI. Bump version and prepare a new signed candidate for every Android source change; stale APKs fail verification.

The earlier v0.1 candidate was signed with a different, disposable CI debug key. That private key is unavailable, so Android cannot install v0.2 over that particular APK. Export v0.1 progress first, uninstall once, install v0.2, restore the backup, then create an account. Original IDs are preserved. Subsequent v0.2+ releases can update in place with this permanent signer. Actual phone upgrade behavior still requires the documented device check.

## Optional GitHub Actions signing

When local signing cannot run, configure the existing recovery archive as one
repository Actions secret named `AE_SIGNING_RECOVERY_ZIP_B64`. This sends the same
private signer to GitHub's hosted runner through its encrypted secret store.
It does not create a new key or change update identity. Never put this value in
source, an issue, a workflow input, a log or a release attachment.

On Windows, copy the archive's Base64 to your clipboard:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$env:USERPROFILE\Downloads\AE-Prepware-Private-Signing-Recovery.zip")) | Set-Clipboard
```

Open repository Settings → Secrets and variables → Actions → New repository secret,
use the name above and paste its value. Then run “Verify and publish signed candidate”
on `main` from Actions, or rerun its verify job. The connected editing tools cannot
set repository secrets; the account owner must configure this once.

Only main pushes and manual runs on main can use the signing secret. Pull requests
and tag-only runs do not receive it. After all source tests/builds/audits pass, the
runner restores the bounded archive outside the checkout, masks decoded passwords,
signs with the pinned permanent certificate, packages it, and checks the entire APK
payload and metadata before publication. Private files are deleted when signing
exits, including failure. Only public APKs/certificates/verification output enter artifacts.
If the secret is absent, source checks still run and publication stays blocked.
A wrong signer or invalid archive fails the job. Existing prepared candidates and
published releases remain preserved.

The public bank is the only bank eligible for this public release workflow.
A private IN build still uses the separate private-candidate process.
