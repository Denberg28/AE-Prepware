# Fresh release signer

On 17 November 2026 the user explicitly authorized a new signing identity and a fresh release, superseding the previous continuity requirement. The pending target is v0.8.3-rc.1 (versionCode 12). Package remains `ph.diversify.aeprepware`. The prior key is retired for future builds; no prior recovery archive is needed.

**Status: replacement permanent key activated for local signing on 18 November 2026.** Its private recovery archive is retained outside git. The new public certificate is pinned in release.json. The Actions signing secret was not changed; CI verifies and publishes locally prepared candidates without needing the private key. A passing unsigned build alone is not an installable release.

## Local signing without GitHub secret access

The authorized replacement key has already been generated. Reuse its private recovery archive; do not run create again. After privately restoring that archive outside the checkout, local activation needs Python/JDK but no GitHub login:

```sh
python scripts/fresh_signer.py activate /private/path/AE-Prepware-Fresh-Signing-Recovery.zip --local-only
```

This validates the real keystore and pins its public certificate, including the retired-key rejection. It does not upload credentials or configure Actions secrets. Commit the public pin/certificate before building. Build the exact committed source, sign with scripts/sign_release.py, package with scripts/package_candidate.py, and commit the prepared candidate. The existing main workflow independently rebuilds and verifies the APK payload, signature, source identity and checksums before publishing a test prerelease. If a candidate is absent, unattended CI signing still needs the matching encrypted secret.

The default activation command below remains available to configure that same key for unattended CI signing later. It must use the same retained archive, not generate another identity.

## Optional Actions secret setup

Requirements: Python 3.10+, JDK 17+ (`keytool` on PATH), Git and authenticated GitHub CLI with permission to set repository Actions secrets (`gh auth login`). Use a current clean checkout of `Denberg28/AE-Prepware` on main. The Android SDK is unnecessary for key setup; the existing GitHub workflow builds the app.

Run in PowerShell from the checkout root:

```powershell
git pull --ff-only
python scripts/fresh_signer.py create "$env:USERPROFILE\AE-Prepware-Fresh-Signer"
python scripts/fresh_signer.py activate "$env:USERPROFILE\AE-Prepware-Fresh-Signer\AE-Prepware-Fresh-Signing-Recovery.zip"
git add release.json signing/AE-Prepware-release-certificate.pem
git commit -m "Activate fresh permanent release signer"
git push origin main
```

The create command generates a permanent RSA-3072/PKCS12 key and a random password, then saves the private recovery ZIP outside the repository. Back up that private directory offline. Use a private user-profile directory with appropriate OS permissions; do not use a shared/cloud-public folder. Existing directories are never overwritten. If creation fails, inspect and preserve any generated files before choosing another directory.

Activation validates the actual keystore, uploads the recovery ZIP to encrypted Actions secret `AE_SIGNING_RECOVERY_ZIP_B64` via GitHub CLI stdin, replaces only the public certificate/digest, and clears the pending-reset flag. Passwords and private archive contents are never printed or committed. A secret-upload failure leaves the public pin unchanged; retry the activate command with the same ZIP. Do not run create again for routine builds.

The secret and public-pin update span separate systems. If activation or the following push is interrupted, retain the private directory, retry activation with the same ZIP, inspect/commit the two public files and push. A mismatched secret/pin fails signing instead of publishing. The connected repository tools cannot set repository secrets. Use local signing when no authenticated GitHub CLI is available.

## Build and publish

The main push runs the existing required Node/Python/browser tests, dependency audits, Android debug/release assembly and lint. It verifies an existing locally prepared candidate, or restores the matching secret outside the checkout to sign a new APK. Verification checks the pinned certificate, package/version, source digest, checksums and exact rebuilt APK payload. Only a verified candidate is eligible for GitHub prerelease publication.

For local Android SDK signing after activation, use `scripts/sign_release.py --credentials /private/path/signing-recovery.json`, then `scripts/package_candidate.py --apk /path/to/signed.apk` and `scripts/package_candidate.py --verify`. Source must be committed. Never attach recovery ZIPs, keystores or passwords to public releases, CI artifacts, logs or git.

## Fresh-install migration

1. Export progress, matching question bank and account recovery from the old app. Preserve unsynced work in a backup.
2. Uninstall the old-signer app only after checking the backups.
3. Install the new-signer candidate and import compatible backups. Verify accounts, scores and unfinished sessions on a test phone.

Android cannot install the replacement-signer APK over the prior app as an ordinary update. This signer change does not require deleting learner data on the server. Subsequent releases must reuse the new permanent key with higher versionCode. Actual phone migration, accessibility and independent faculty review remain pending, so this remains a test candidate.

Earlier releases are historical until a replacement is verified; they are not inputs to the new signing process. See [current checkpoint](../docs/STATUS.md) for built/published status.

Implementation references: [JDK keytool](https://docs.oracle.com/en/java/javase/21/docs/specs/man/keytool.html), [GitHub CLI secret setup](https://cli.github.com/manual/gh_secret_set).
