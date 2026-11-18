# AE Prepware v0.8.3-rc.1 · Review-focused test candidate

Continue and compact subjects lead the app; optional setup is grouped under Practice options. Results shows scores and history first, with monitoring in an optional panel. Submitted sessions show expanded mistakes first and keep correct answers and explanations accessible. A timing issue that could close practice options during a selection is fixed.

Cleaner subject cards with local icons and clearer PRC weight badges, labeled navigation icons, more readable question spacing and larger answer targets. Refined light/dark surfaces support small screens and enlarged text while the header and navigation remain fixed.

Selected answers show “Your answer,” including diagnostics and spaced rechecks without revealing correctness before submission. Keyboard focus follows questions and answer feedback. Confirmation dialogs have accessible names, and unavailable question pools explain how to continue.

Question content, grading keys, source quotas, accounts, saved progress, unfinished sessions and sync formats are preserved. Aerodynamics retains its existing bearing, heading and throat exercises within the normal subject. No new runtime dependencies.

## Fresh signing identity

The authorized replacement permanent key was generated, privately backed up and activated for local signing on 18 November 2026. The retired key is not used. Export progress, matching bank and account recovery before uninstalling the old-signer app, then install the new-signer APK and import compatible backups. Android cannot update across signing identities in place. Package identity and learning-data schemas remain unchanged. Keep the new private recovery archive for every future release; never publish it.

## Build and publication status

Version: 0.8.3-rc.1; versionCode: 12; package: ph.diversify.aeprepware. The review-flow source at 1501b5eb11c9b020f631b0434613254141cd840e passed all required source, browser/service, dependency-audit, Android assembly and lint checks in workflow 44298938071. PR #5 is merged. Signing-path checks run again on the activated-source commit.

The local signing route does not require GitHub login or a repository-secret change. The prepared APK must pass scripts/package_candidate.py --verify, including the pinned certificate and exact rebuilt payload, before the existing workflow publishes it. Published candidates include their APK, SHA-256 checksum, public certificate and verification metadata. Private signing material stays outside git and release assets.

The previous signed v0.8.2 candidate is retained. Before installing a future signed update, export progress and the matching bank; perform the documented backup/uninstall/fresh-install migration for the new signing identity. Physical Android installation/update, TalkBack, native font scaling and system-bar checks remain pending. Independent faculty review and production hosting remain pending. This is not a stable release.
