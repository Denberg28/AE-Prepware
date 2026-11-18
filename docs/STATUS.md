# AE Prepware checkpoint

Updated: 18 November 2026 (Asia/Manila).

## Current goal and baseline

Simplify AE Prepware into a focused review tool. Repository `Denberg28/AE-Prepware`, source baseline `92e9605` on main. Authorized scope includes reviewed source commits/pushes and eligible prereleases. The existing unpublished version remains 0.8.3-rc.1 / code 12. Preserve the current signing reset guard, banks, scores, local profiles, unfinished sessions and sync contracts.

## Implemented

- Continue and compact subjects lead the study flow; Practice options groups scope, AI/IN sources and selection. Optional panels start collapsed and keep their open state through in-page re-renders.
- Results leads with scores and session history; existing checks and monitoring remain in an optional disclosure.
- Submitted session review expands mistakes first and keeps correct answers in a separate disclosure. Explanations remain optional; deferred checks still withhold keys until submission.
- Updated existing browser journeys for explicit disclosure opening; added mixed-score/all-correct review assertions. See UI_REFINEMENT.md and CODE_EDIT_GUIDE.md.

## Verification

**PASS:** `node --test tests/*.test.cjs` — 41 tests; `python -m pytest -q` — 60 tests; JS syntax and `git diff --check`. npm audit reports zero vulnerabilities. These are local source checks, not device evidence.

**BLOCKED locally:** Chromium exits before launch because a required socket operation is denied; downloaded Playwright Headless Shell archives could not be retrieved intact. Gradle bootstrap fails with `Network is unreachable`; no local Android build/lint evidence. Full browser and Android checks must run in the existing PR CI before promotion. CI results belong to their actual source SHA.

**Existing release blocker:** `release.json:signerResetPending` is true. Fresh permanent signing was authorized on 17 November; production key activation/Actions secret configuration and signed publication are not completed. This layout change does not generate or rotate a key. Use signing/README.md for the existing activation procedure.

**NOT TESTED:** physical Android layout, TalkBack, native font/system bars/lifecycle, migration/in-place update under the new signer, independent faculty content review and live hosting. Stable promotion remains blocked. Rollback is a focused revert to baseline; no data migration is introduced.

Next step: complete the review branch CI, resolve observed failures, and keep signed publication gated until the existing permanent-key setup is activated.
