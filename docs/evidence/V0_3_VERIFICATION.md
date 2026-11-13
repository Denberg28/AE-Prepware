# v0.3.0-rc.1 verification · 2026-11-13

Baseline: public main `bdbe63d`, signed v0.2.0-rc.1. The reported unfinished
AI/IN implementation and 2,005-question IN import were not in any recoverable
branch/workspace. This change implements the workflow on the published baseline;
it does not claim recovery of that corpus. The bundled bank remains 360 original
AI foundation questions, with independent faculty review pending.

Scope: AI/IN labels and exact source selection; admin-only reviewed corrections;
validated IN import; append-only Android refresh; archived API grading keys.
Acceptance: 50 distinct questions, Hybrid 25 each, unavailable pools block,
non-admin edits unavailable, existing keys immutable, scores/queues/current
session preserved, old-bank submissions graded after API restart.

Self-reviewed software evidence (not independent faculty or physical validation):

| Gate | Status | Evidence |
| --- | --- | --- |
| A/B/C JS core/account/source | PASS | 21 Node tests; original keys, locks, queues, provenance, exact quotas, immutable refresh |
| A/B/D Python | PASS | 25 pytest tests; actual Streamlit admin sign-in/edit/signout, IN sanitation, real SQLite archived-key restart/grading and source selection |
| B/C browser study | PASS | Existing 50-question score/feedback, recovery/isolation, saved order, backup/corruption/legacy workflow |
| B/C browser source refresh | PASS | Empty/no-source blocks, refresh cancel/confirm, original-key ongoing session, historical 50/50 score, 25+25 quota, tamper rejection, later full snapshot on a new device, reused-version rejection, 320 px layout |
| D account integration | PASS | Actual local API/SQLite, dropped-ack retry, grade/ranking, cloud recovery; HTTPS origin simulated |
| A dependency audits | PASS | pip-audit locked backend and npm audit: no reported vulnerabilities |
| A Android | PASS | Debug/release assemble and lint, SDK 35/build-tools 35.0.0, Gradle 8.10.2, JDK 21.0.13 |
| F permanent signer/package | See release manifest/APK-VERIFICATION | Package script verifies certificate, versionCode 3, non-debuggable manifest, source digest, checksum and full rebuilt payload |
| E/F physical Android install/update/SAF/accessibility | NOT TESTED | Requires user device; same-certificate static checks do not satisfy installation/update testing |
| D production HTTPS/live provider | NOT TESTED | No new hosted deployment/provider-key validation |
| Faculty validation | BLOCKED | Independent qualified review and instructor corpus required |

Tests use synthetic IN fixtures only; these are not included as scored content.
No passwords, recovery codes, signing keys or restricted PDFs enter public git.
Admin Secrets must be configured independently; editing defaults to disabled.
Exports persist dashboard work; unexported session memory is temporary. API
SQLite snapshots preserve old keys only for versions it has archived. Unknown
versions fail with 409 while keeping device queues intact.

Candidate only. Preserve v0.2 and matching bank/progress backups. Android blocks
downgrades; uninstalling erases app data. Device upgrade, import, lifecycle and
accessibility checks in TESTING.md remain required before stable promotion.
