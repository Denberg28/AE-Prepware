# AE Prepware checkpoint

Updated: 17 November 2026 (Asia/Manila).

## Authorized goal and baseline

The user explicitly requests a new release with a new signer, discarding the prior signing identity and starting fresh. This supersedes the earlier continuity-only decision. Reviewed commits, pushes and eligible GitHub prerelease publication remain authorized. Package `ph.diversify.aeprepware`, question banks, account/progress formats and server records remain intact; the signer change requires a one-time phone backup/uninstall/reinstall.

Repository: `Denberg28/AE-Prepware`, main. Baseline source: `2afa8c1d19b0a1a7ec7a7081db09c562cfc684e5`. Pending release: v0.8.3-rc.1, versionCode 12. Existing historical signed releases are not inputs to new-key setup. AGENTS v1.4, kickoff v1.3 and constitution v3.2 are already adopted with AE Prepware project rules preserved.

## Implemented

- `scripts/fresh_signer.py` creates a permanent RSA-3072/PKCS12 key with a random password and private recovery ZIP outside the checkout. It refuses overwrites. Activation validates the actual keystore, configures the encrypted Actions secret via GitHub CLI stdin and replaces only the public pin/certificate.
- `release.json:signerResetPending` blocks CI and direct signing until new-key activation; activation rejects the retired certificate. No old recovery archive is required.
- Signing/migration documentation and project rules now reflect the authorized reset. Private key generation/activation is deliberately separate from public source.
- Integration checks cover a real temporary key, recovery round-trip, secret-upload failure preserving the pin, secret stdin handling, overwrite/checkout protection and pending-reset guards. Temporary test keys are never production keys or release assets.

## Evidence and remaining work

**PASS / build verified baseline:** [workflow 43972952750](https://github.com/Denberg28/AE-Prepware/actions/runs/43972952750) on baseline source completed successfully. This does not verify the new setup code; consult the maintenance PR/CI for its results.

**BLOCKED: production key creation, activation and signed release.** This session has no usable local execution environment and cannot configure repository Actions secrets. No new production key, signed APK or GitHub release has been created. The old certificate stays historical in source until activation replaces it; the reset flag prevents its use by the release signer.

**Next executable step:** run the [fresh signer setup](../signing/README.md#create-and-activate-once-on-your-computer) in a local checkout with Python, JDK and authenticated GitHub CLI. Privately back up the resulting recovery directory. Commit/push only the public certificate and release.json; the existing release workflow then builds, signs, verifies and publishes an eligible prerelease.

**NOT TESTED:** physical Android migration/in-place updates within the new signer, TalkBack/native font/system-bar behavior, independent faculty content approval and production hosting. These continue to block stable promotion.
