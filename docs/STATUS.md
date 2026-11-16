# AE Prepware checkpoint

Updated: 17 November 2026 (Asia/Manila).

## Scope and baseline

User request: adopt the latest kickoff, agent and constitution guidance and prepare signing for the new release. Reviewed commits/pushes and eligible GitHub prereleases are authorized; private signing identity and private IN content remain protected.

Repository: `Denberg28/AE-Prepware`, `main`. Baseline source: `753b149a1cf253ae62d5ef647fcb029821e69e9c`. Latest published signed release: [v0.8.2-rc.1](https://github.com/Denberg28/AE-Prepware/releases/tag/v0.8.2-rc.1). Current release configuration: `release.json` (v0.8.3-rc.1, versionCode 12 at this checkpoint). The prior published version is retained for recovery.

## Completed and evidence

- Adopt AGENTS v1.4, kickoff v1.3 and constitution v3.2 from [shared revision 012797d58ae19c713b7051f233d4023db94afd67](https://github.com/Denberg28/Agents_md/tree/012797d58ae19c713b7051f233d4023db94afd67); retain all existing AE Prepware rules.
- Add a targeted edit guide and filled project kickoff, reference standing GitHub publication authorization, and retain the existing signer rather than create a second identity.
- Review current signing scripts and release workflow. The existing pipeline already restores a private archive, signs with the pinned certificate, verifies exact rebuilt APK content, and publishes only eligible prepared candidates.
- **PASS / build verified:** [baseline workflow 43969274307](https://github.com/Denberg28/AE-Prepware/actions/runs/43969274307), source `753b149a1cf253ae62d5ef647fcb029821e69e9c`: Node/Python tests, browser workflows, dependency audits and Android debug/release assembly/lint. This is baseline evidence; any subsequent run has its own result.
- **REVIEWED:** this maintenance patch changes documentation only. Android inputs, signing scripts, package identity, version/code and grading/storage contracts are preserved. No local execution environment was available during this maintenance session.

## Blocker and next executable step

**BLOCKED: signed v0.8.3 publication.** Baseline workflow verify job 133656817993 reports: “Signing secret is not configured; signed publication remains blocked.” The publication job was skipped. No signed v0.8.3 APK or release was produced.

The private recovery archive is available as `AE-Prepware-Private-Signing-Recovery.zip`; possession of the public certificate alone cannot sign. Connected repository editing cannot configure Actions secrets, and the current session has no local execution environment for private signing.

Repository owner: follow [signing setup](../signing/README.md#optional-github-actions-signing) to set `AE_SIGNING_RECOVERY_ZIP_B64` from that existing ZIP, then run “Verify and publish signed candidate” on main. Check every required gate, the published APK fingerprint/checksum, version and release assets. Never substitute a new/debug key to bypass this blocker.

**NOT TESTED:** physical Android installation/in-place update, TalkBack/native font/system-bar behavior, independent faculty content approval and production hosting. These continue to block stable promotion. Before a phone update, export progress and matching bank, then install the same-signer candidate without uninstalling; retain the prior APK and matching backups for rollback.
