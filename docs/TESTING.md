# Verification gates

Run from repository root. Evidence labels are distinct: reviewed, build verified, desktop simulated, Android-device tested, field validated. A browser test is not a phone test. No physical control or custom hardware is involved, so motor/link HIL is N/A; Android lifecycle/device validation is required for stable.

## Required candidate gates

| Gate | Command/procedure | Required result |
| --- | --- | --- |
| A: bank/core | `node --test tests/*.test.cjs` | all pass; six weights/72 items, correct shuffle and XP |
| A: Python | `.venv/bin/python -m pytest -q` | bank/API grading, ownership, rejection, expiry, privacy, CORS pass |
| A: dependencies | `.venv/bin/pip-audit -r backend/requirements.lock`; `npm audit --audit-level=high` | no reported high/critical unresolved vulnerabilities |
| A: Android | `./gradlew :app:assembleDebug :app:assembleRelease :app:lint` | both variants compile, lint has no errors |
| B/C: UI | `npm ci`; `npx playwright install chromium`; `node tests/browser.cjs` | mobile flow, resume, results, mock feedback, escaping, corruption recovery pass |
| D: service | API test client and UI mock-service integration | no duplicate credits; token/participant isolation; useful offline errors |
| F: packaging | `python scripts/package_candidate.py` | package/API/version/signature inspected; APK <5 MB; checksums/source identity |

No earlier baseline exists; regression fixtures establish the first baseline. Browser suite tests 393×851 and 320×640, no horizontal overflow or uncaught JS errors. Device timing and lifecycle behavior remain independent checks.

## Required stable checks — run on an Android phone

Record model, Android version, System WebView version, APK SHA-256 and commit. All expected results must pass; attach observations to a follow-up issue/report.

1. Install candidate (allow unknown source for the installing app). Confirm launcher identity/version. Cold start five times in airplane mode; home should render in ≤3 seconds and answer/next respond in ≤250 ms on the tested device. Record actual timing, not an estimate.
2. Start a ten-question session. Answer once, tap repeatedly, verify one attempt and a single locked choice. Background/resume five times, rotate three times, then force-stop and reopen. Verify exact question/choice/order, no extra XP and no lost answer.
3. Complete a weighted short check; explanations appear only at submission. Compare 20-item 2/5/4/3/4/2 distribution, totals and explanations against bank JSON.
4. Use ☆ Save, mistake review and set-aside/report. Set aside enough questions to make a weighted check impossible; verify clear message and restoration recovery.
5. In Settings, export via Android document picker. Cancel once, then save. Record file opening/filename. Import a valid backup, cancel replacement once, then confirm; confirm session/progress unchanged after cancellation and restored after confirmation. Import malformed JSON/wrong version/>2 MB: show error and preserve current progress.
6. Test 320 dp small phone and tablet/landscape with system font scale 1.0 and 1.5, talkback labels, navigation bar/cutout/keyboard; every answer and next control reachable, no clipped text.
7. On a disposable test installation, clear WebView/app data only after exporting. Restore backup. Confirm uninstall warns through documentation and requires backup for later recovery. Simulate low disk; save error blocks additional answers and raw export remains accessible.
8. Start optional API behind HTTPS with a persistent SQLite database. Two phones join using different names. Complete challenges; check server score/rank, one daily credit per question, retry after dropping network at submission, 12-second timeout and resumable answers. Reconnect must not double-credit. Stop/restart API and verify standings survive. Delete one account and verify cascading removal.
9. Install same-signer higher-version test build over candidate and verify data continuity. Different debug signer is expected to require backup/uninstall/reinstall; validate before any production promotion. Never reuse this candidate version for a different APK.
10. Qualified instructors independently check each question, explanation, assumptions, source locator and current law. Export a new approved bank and verify Android import/version matching with API. Run live optional AI with a configured key and inspect its draft label, content/failure recovery. AI correctness is not inferred from provider success.

## Faults and release tiers

Candidate requires automated gates above; missing real Android, hosted HTTPS and live AI evidence is disclosed. No known critical/high code defects may be released. Stable is blocked until all applicable device/content checks pass. AI remains optional; absence of credentials does not disable offline learning. Hosted endpoint is an operator deployment, not presumed available.

See `docs/evidence/VERIFICATION.md` for this candidate's actual status, environment and limitations. Logs/screenshots are packaged by CI and release artifacts, never described as physical test evidence.
