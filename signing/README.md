# Permanent APK signer — v0.2 onward

The public certificate in this directory pins the AE Prepware update identity. Its SHA-256 digest is in `release.json`. Package name stays `ph.diversify.aeprepware`. v0.2.0-rc.1 has versionCode 2; future updates must raise versionCode and use the same private key/certificate.

The user explicitly authorized permanent signing on 2026-11-13. Private key and password are in the private **AE-Prepware-Private-Signing-Recovery.zip** recovery archive, not this public repository. Keep that archive private and backed up offline. The public certificate alone cannot sign updates.

Restore recovery files to a private directory outside the repository, then:

```sh
./gradlew :app:assembleDebug :app:assembleRelease :app:lint
python scripts/sign_release.py --credentials /private/path/signing-recovery.json
# Commit final source before packaging; the source tree must be clean.
python scripts/package_candidate.py --apk artifacts/AE-Prepware-0.2.0-rc.1-Signed-Candidate.apk
python scripts/package_candidate.py --verify
```

Set `ANDROID_HOME` to the SDK with build-tools 35.0.0. Signing reads passwords from private file into process environment; values are not printed or embedded in the APK. Do not pass passwords on the command line, commit recovery files, or upload them to GitHub Releases.

Prepared signed APKs and public verification metadata under `release-candidates/<version>/` are public. CI runs all tests, builds the unsigned release, verifies the permanent certificate, source digest, exact unsigned ZIP payload (apart from Gradle's VCS marker), version, checksum and packaged assets. Only then does it publish the same signed candidate. Keeping prepared signed binaries in source makes this small project releaseable without sending the private key to CI. Bump version and prepare a new signed candidate for every Android source change; stale APKs fail verification.

The earlier v0.1 candidate was signed with a different, disposable CI debug key. That private key is unavailable, so Android cannot install v0.2 over that particular APK. Export v0.1 progress first, uninstall once, install v0.2, restore the backup, then create an account. Original IDs are preserved. Subsequent v0.2+ releases can update in place with this permanent signer. Actual phone upgrade behavior still requires the documented device check.
