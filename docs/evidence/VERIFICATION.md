# Candidate verification — 2026-11-13

Scope: initial AE Prepware 0.1.0-rc.1 source; exact commit is written into release-manifest.json and APK-VERIFICATION.txt during packaging. Self-review only; no external reviewer or physical-device evidence is claimed.

Environment: Linux x86_64; Amazon Corretto JDK 21.0.13; Gradle 8.10.2 checksum verified; Android SDK 35/build tools 35.0.0; Python 3.12 isolated venv; Node 24; Playwright (lock pinned) using Chrome headless shell 131 for local UI simulation. CI uses its pinned Playwright browser.

| Gate/check | Status | Evidence/meaning |
| --- | --- | --- |
| A: Android debug/release compilation | PASS | Gradle assembleDebug + assembleRelease; release variant unsigned |
| A: Android lint | PASS | 0 errors; JavaScript enablement warning reviewed: local packaged UI requires it, remote navigation excluded and output escaped |
| A/B: core/bank invariants | PASS | 12 Node tests, 72 records, six weights, sampling, answer lock, spacing, XP, state validation |
| B/C/D: API and bank | PASS | 7 pytest tests: actual SQLite transactions, server grading, retries, ownership, deletion, malformed input, limits/expiry, CORS |
| B/C: mobile browser study | PASS | 393×851 and 320×640: study, restart/resume, results, deferred mock feedback, display-name escaping, invalid backup rejection, cancellation/confirmed restore, preserved corrupt record |
| D: cohort UI to local API | PASS | Real local FastAPI/SQLite with simulated HTTPS origin, challenge flow, submit and leaderboard; no live TLS validation claim |
| D: private Streamlit UI | PASS | AppTest launch, three tabs, coursework/review controls without exception; optional AI disabled without configuration |
| A: dependency security | PASS | pip-audit lock: no known vulnerabilities after pytest upgrade; npm audit: 0 vulnerabilities |
| A: source/configuration self-review | PASS | No runtime Android third-party dependency, no keys/tokens/signing files tracked; content escapes, HTTPS limits and import gates reviewed |
| F: APK signature/manifest/size | PASS | package_candidate.py verifies APK signature, package/API/version, <5 MB and SHA-256; exact output recorded alongside APK |
| E: custom physical-control HIL | N/A | Educational app; no motor, aircraft or custom hardware control path |
| E/F: physical Android/device installation | BLOCKED | No Android device connected; use docs/TESTING.md, includes picker/lifecycle/upgrade/accessibility and timings |
| Content: independent faculty item audit | BLOCKED | Author source-checks only; original foundations, not complete syllabus coverage |
| D: live hosted HTTPS service | NOT TESTED | Included runnable service has not been provisioned or deployed |
| D: live Gemini coursework generation | BLOCKED | No provider key/model configured; draft request path and error handling reviewed only |
| Stable promotion | BLOCKED | Physical Android and independent content review outstanding |

Packaging attaches source SHA, checksum, signer fingerprint and compatibility. Test candidate eligibility does not imply stable readiness. CI evidence is separate from these local results; do not claim CI passed before observing the remote run.
