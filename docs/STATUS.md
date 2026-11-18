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

**PASS / activated-source build:** workflow [44332121392](https://github.com/Denberg28/AE-Prepware/actions/runs/44332121392) passed all gates with 62 Python tests, 41 Node tests, 11 browser/service workflows, audits and Android assembly/lint. The actual reviewed CI checkout and APK source revision is `90017bf7cc8ed485396e609655f047e05485b3d0` (PR #6 test merge); the prepared-candidate commit descends from this reviewed source.

**PASS / signed candidate prepared:** replacement permanent key generated once, privately backed up outside git and locally activated. Candidate v0.8.3-rc.1 / code 12 is in `release-candidates/0.8.3-rc.1/`. Local packaging verification passed certificate, manifest, checksum, source digest, bundled assets and exact rebuilt unsigned payload. APK SHA-256: `13ef21356e0f59d789cf9c7b7b95b0dc23014f82d9243adc846d3d2356cdd7db`. Permanent signer: `760d4e46423c13d4ce6fb79e9d976c3ecf3dc0d0054774c8a2b30ef94f4d3d13`. The retired certificate is not used; no private key or password is committed or published. The optional Actions signing secret is unchanged. Future versions reuse this retained identity.

**NOT TESTED:** physical Android layout, TalkBack, native font/system bars/lifecycle, migration/in-place update under the new signer, independent faculty content review and live hosting. Stable promotion remains blocked. Rollback is a focused revert to baseline; no data migration is introduced.

Publication gate: CI independently rebuilds this prepared candidate and checks its signature, source identity and payload before eligible main-branch prerelease publication. Use the final PR/workflow/release record for the observed publication result; packaging alone does not imply publication.
