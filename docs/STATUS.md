# AE Prepware checkpoint

Updated: 18 November 2026 (Asia/Manila).

## Current goal and baseline

Simplify AE Prepware into a focused review tool. Repository `Denberg28/AE-Prepware`, source baseline `92e9605` on main. Authorized scope includes reviewed source commits/pushes and eligible prereleases. Release target remains 0.8.3-rc.1 / code 12. PR #5 is merged as 7ef5e9d. Preserve banks, scores, local profiles, unfinished sessions and sync contracts.

## Implemented

- Continue and compact subjects lead the study flow; Practice options groups scope, AI/IN sources and selection. Optional panels start collapsed and keep their open state through in-page re-renders.
- Results leads with scores and session history; existing checks and monitoring remain in an optional disclosure.
- Submitted session review expands mistakes first and keeps correct answers in a separate disclosure. Explanations remain optional; deferred checks still withhold keys until submission.
- Updated existing browser journeys for explicit disclosure opening; added mixed-score/all-correct review assertions. See UI_REFINEMENT.md and CODE_EDIT_GUIDE.md.

## Verification

**PASS / build verified:** workflow [44298938071](https://github.com/Denberg28/AE-Prepware/actions/runs/44298938071) on source `1501b5e` completed all required Node/Python, 11 browser/service workflows, dependency audits, Android debug/release assembly and lint. Disclosure state is captured synchronously before rendering; regression journeys explicitly open options/monitoring after reload.

**Signing in progress:** replacement permanent key generated once, private recovery retained outside git, public certificate locally activated. The retired certificate is rejected. `activate --local-only` supports the existing prepared-candidate CI path without changing Actions secrets or requiring browser login. New signer fingerprint: `760d4e46423c13d4ce6fb79e9d976c3ecf3dc0d0054774c8a2b30ef94f4d3d13`. Build the activated-source commit, sign and package that exact APK, then commit only public candidate assets for CI verification/publication. No private key or password belongs in git, CI artifacts or public releases.

**NOT TESTED:** physical Android layout, TalkBack, native font/system bars/lifecycle, migration/in-place update under the new signer, independent faculty content review and live hosting. Stable promotion remains blocked. Rollback is a focused revert to baseline; no data migration is introduced.

Next step: verify the local-signing source in CI, download its unsigned release, sign/package the exact source commit, and submit the prepared public candidate for independent CI verification before publication.
