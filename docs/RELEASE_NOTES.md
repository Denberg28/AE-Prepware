# AE Prepware v0.8.3-rc.1 · UI update

Cleaner subject cards with local icons and clearer PRC weight badges, labeled navigation icons, more readable question spacing and larger answer targets. Refined light/dark surfaces support small screens and enlarged text while the header and navigation remain fixed.

Selected answers show “Your answer,” including diagnostics and spaced rechecks without revealing correctness before submission. Keyboard focus follows questions and answer feedback. Confirmation dialogs have accessible names, and unavailable question pools explain how to continue.

Question content, grading keys, source quotas, accounts, saved progress, unfinished sessions and sync formats are preserved. Aerodynamics retains its existing bearing, heading and throat exercises within the normal subject. No new runtime dependencies.

## Build and publication status

Version: 0.8.3-rc.1; versionCode: 12; package: ph.diversify.aeprepware. The UI commit b1cb4dd53cdf4a14912d27602895ec5a6ea956d0 passed Node/Python tests, all 11 browser workflows, dependency audits, Android debug/release assembly and lint in workflow run 43963405907. PR #1 is merged; main builds retain the same required gates.

Signed publication requires the existing permanent certificate and scripts/package_candidate.py --verify. GitHub Actions can prepare the APK using the optional encrypted AE_SIGNING_RECOVERY_ZIP_B64 repository secret; see signing/README.md. Without that secret or a locally prepared signed candidate, publication stays blocked. Published candidates include their APK, SHA-256 checksum, public certificate and verification metadata. The release workflow never publishes an unsigned APK as an installable candidate.

The previous signed v0.8.2 candidate is retained. Before installing a future signed update, export progress and the matching bank; install the new same-signer APK without uninstalling. Physical Android installation/update, TalkBack, native font scaling and system-bar checks remain pending. Independent faculty review and production hosting remain pending. This is not a stable release.
