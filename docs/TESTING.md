# Verification gates — v0.3.0-rc.1

Scope/acceptance is in V0_2_SCOPE.md. Candidate gates below run on final source; physical Android and faculty review block stable promotion. No motors or custom hardware are controlled, so physical-control HIL is N/A. Desktop simulation is not phone testing.

| Gate | Command/procedure | Acceptance |
| --- | --- | --- |
| A/B: core/account | `node --test tests/*.test.cjs` | all pass: 360 items/60 per subject, 50 unique selections, wrong/duplicate locks, saved order/score/queue, account isolation and legacy progress |
| A/B/D: Python | `python -m pytest -q` | API grading/ownership, scrypt recovery, expiry/logout/deletion, retry conflict, daily credits, bank arithmetic/old IDs, Streamlit Secrets/UI, allowlisted AI/fallback pass |
| A: dependencies | `pip-audit -r backend/requirements.lock`; `npm audit --audit-level=high` | no unresolved high/critical findings |
| B/C: mobile UI | `mkdir -p artifacts`; `node tests/browser.cjs` | six subjects, exact 50-item score, correct shuffled letter, collapsed explanation, resume, account binding/recovery, backup cancellation/restore, corruption and old-session migration |
| D: actual local service | `node tests/cohort-browser.cjs` | real API/SQLite: create/connect, 50-item server grade, dropped-response retry does not duplicate, leaderboard, AI fallback and new-device cloud recovery |
| A: Android | `./gradlew :app:assembleDebug :app:assembleRelease :app:lint` | debug/release compile, lint no errors; unsigned release non-debuggable |
| F: permanent signer | `python scripts/sign_release.py --credentials /private/path/signing-recovery.json` | permanent key matches public certificate/release.json; v2/v3 signature verifies |
| F: packaging | `python scripts/package_candidate.py --verify` | pinned signer/version/package/checksum/source digest/assets and full rebuilt unsigned ZIP payload match |
| F: update certificate | build temporary versionCode3 test APK, sign with same key, inspect manifests/certs | higher code and identical certificate; no private key in APK/repo. This is static/build evidence, not on-phone update validation |

Browser tests use 393×851 and 320×640 and check no horizontal overflow or uncaught errors. CHROMIUM_PATH can select a system Chromium; AE_PYTHON can select the integration API interpreter. CI runs the same software checks and publishes only prepared signed artifacts that pass. Source-only CI without a signed artifact must skip publication.

## Required Android device validation before stable

Record device, Android/System WebView versions, APK hash and certificate fingerprint, source commit and configuration. Attach actual observations/timings; do not infer from screenshots or signatures.

1. Export v0.1 progress before uninstalling its debug-signed APK. Install v0.2, restore guest backup and verify original records/session. Create account and save recovery file. The first signer transition is an intentional one-time reinstall; private v0.1 CI key is unavailable.
2. Cold start five times in airplane mode (target ≤3 s), choose each subject, confirm 50 distinct same-subject IDs and shuffled choices. Answer/next response target ≤250 ms on tested device. Incorrect selection shows correct displayed letter/text; correct selection locks/marks correctly; explanations start closed and expand accessibly.
3. Complete 50 with a known mix of answers and compare exact score/history after force-stop/reopen. Repeated taps cannot double-credit. Save/exit, background/resume five times, rotate three times; exact saved question/answer/order persists.
4. Create two local accounts, record different results, sign out/in using recovery files, verify isolation. Wrong number/code rejected. Account number alone cannot sign in. Guest and account backup imports cannot cross-bind. Keep code private; code cannot be reconstructed from the local verifier.
5. Test SAF export/import for progress and account recovery; cancel and retry; wrong account/bank, malformed JSON and >8 MB rejected without changes. Recover a deliberately corrupted disposable profile only after exporting raw data. Simulate low disk: saving error must block further answers and expose recovery export, not overwrite valid persisted progress.
6. Test 320 dp phone/tablet/landscape, font scaling 1.0/1.5, TalkBack, keyboard/system bars. All letters, next and explanation controls reachable; no overflow/clipping. Current WebView is required.
7. Host API behind real HTTPS with persistent disk. Two phones restore the same account and sync different sessions; server records correct ownership/grade. Drop network at submission after server commit and retry: same ID counts once. Stop/restart API; records/ranking persist. Offline scores queue; 200 pending blocks new sessions without deleting data. Delete online account: its public rank/results/tokens disappear, local data remains.
8. With authorized provider key/model, request AI topic selection for different histories. Confirm only existing bank IDs, no changed keys, no personal data, useful focus and declared fallback on timeout/quota/malformed response. Live provider access is separately tested from mock success.
9. Install a genuinely higher-version APK signed with the permanent key OVER this candidate. Verify Android accepts update and accounts, progress, queues and imported banks survive without uninstall. Mismatched signer should be rejected. Static same-certificate checks do not satisfy this device gate.
10. Qualified faculty independently verify every item: assumptions/units, one correct answer, explanation, source locator, current law and topic coverage. Export a new approved bank and test matching API/phone import. Restore/sync pending old-bank sessions before replacement.

## Evidence and tier

See evidence/V0_2_VERIFICATION.md. PASS/FAIL/NOT TESTED/BLOCKED refer only to observed checks. Missing phone, live hosting/AI or content checks must be disclosed. No stable promotion or pass guarantee. Preserve the existing release; never reuse a version/tag for changed APK bytes.

## v0.3 source and admin regression

Run `node tests/sources-browser.cjs` after creating artifacts. Synthetic IN fixtures
are test-only and are never bundled. It verifies empty/no-source blocking,
AI/IN source labels, 25+25 Hybrid selection, compatible refresh cancellation and
confirmation, original-key resume/score, tamper rejection and 320 px layout.
`tests/test_authoring.py` uses the actual Streamlit AppTest to verify failed login,
admin-only edit access, reviewed versioned correction, and signout. Actual
FastAPI/SQLite restart tests verify original queued-key grading and source quotas.
The merge tests reject unapproved/unknown-rights/duplicate records atomically.
Python and JS core tests verify old scores/queues/sessions remain valid.

Physical tests must additionally import a reviewed bank using Android SAF,
resume an old-key session, verify AI/IN/Hybrid pools, install this candidate over
v0.2 with the same certificate and confirm profile data survives. Desktop browser
or static certificate checks do not replace these physical-device gates.


## v0.4 private bank/layout checks

Install `scripts/requirements-authoring.lock` for PDF parser tests. Run
`node tests/private-bank-browser.cjs` with original synthetic fixtures in public
CI. For a local private verification only, set `AE_PRIVATE_BANK` to the generated
private bank path; book text is excluded from logs/screenshots. This exercises
3-choice scoring/resume, source-review labels, IndexedDB/account copy, later
public-app upgrade retention, nav contrast, small screens and enlarged text.
The independent Poppler footer check covers all imported keys; it does not
replace faculty semantic review. See evidence/V0_4_VERIFICATION.md.


## v0.4.1 center-only scroll check

`node tests/shell-browser.cjs` checks header/nav positions before and after wheel
scrolling, long-question/feedback scrolling and next/tab changes. It verifies the
document never scrolls, controls remain inside the center pane, settings stay
reachable, removed instructions stay absent, and unfinished session order/answers
survive navigation. Includes 320x480, 393x760 and 720x480 plus enlarged text.
Native system bars remain a physical-phone check; no new phone validation is
inferred from the screenshot used to report this UI change.
