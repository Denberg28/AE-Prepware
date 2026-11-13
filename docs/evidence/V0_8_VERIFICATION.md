# v0.8.1-rc.1 verification

Baseline: public v0.6.0-rc.1, commit c384c6fcd2b18e527e077f0e90b20cac6dbf32d0. The local monitoring continuation was preserved in a separate checkout; this candidate integrates it with full synchronization and feedback calculations. Version code 10 supersedes the intervening continuation candidates. Candidate only.

| Gate | Result | Evidence |
| --- | --- | --- |
| Product principle | PASS / reviewed | Commitment, competence and readiness documented in AGENTS/README, shown on Home and separated under Results. Participation is not a motivation classification; scores do not become pass probabilities. |
| Unit and API behavior | PASS / simulator tested | 41 Node and 44 Python checks: grade locking, first-attempt protection, retention/recency rules, all-six weighting, history compatibility, upload replay/conflicts, owner isolation, consent, deletion, enrollment and private-route protection. |
| Browser regression | PASS / simulator tested | Ten workflows: baseline study, accounts, source refresh, synthetic private bank, steady shell, themes/contrast, compact core, readiness, full sync and combined online host. Real SQLite/API, browser storage contexts and simulated HTTPS routing; no physical-phone claim. |
| Full sync | PASS / simulator tested | Lost-ack retries produce no duplicate scores; in-flight backup is durable; second-device recovery retains journal and unfinished check; stale revision, offline failure and bank tampering preserve local state. Ranking and facilitator sharing are separate opt-ins. |
| Streamlit integration | PASS / simulator tested | Combined ASGI service renders all four tabs with live WebSocket under /dashboard; root API and authenticated owner endpoints work. Admin-gated shared-summary retrieval and server-only key flow covered by Streamlit test. |
| Content | PASS / reviewed and calculator tested | 380 public AI records, unchanged 120 core; 2417 private records, unchanged 240 core. All 2397 prior private grading records retained. 20 new original exercises independently solved from printed givens: 6 bearing, 6 heading, 8 throat. Existing 264 parameterized and 77 core numerical checks pass. AI labels and pending faculty-review metadata remain explicit. |
| Actual private bank | PASS / simulator tested | Three-choice study/restart/grade, IndexedDB persistence, profile binding, subsequent public-app update, contrast and small-screen enlarged-text checks pass with the supplied private bank. No private corpus is published. |
| Android | PASS / build verified | Debug/release assemble and lint, JDK 21, Gradle 8.10.2, SDK/platform and build-tools 35.0.0. Final packages are rebuilt against the source commit and separately verified. |
| Dependencies | Baseline retained | Lockfiles unchanged from the verified v0.6 baseline; no new runtime dependencies. npm current audit reports zero vulnerabilities. Fresh local Python advisory refresh is BLOCKED by PyPI connection timeouts; no clean fresh-audit claim is made. CI retains both locked Python audits and gates publication. |
| Packaging | Separate manifests | Permanent certificate and package identity; version/code, source commit marker, input digest, exact assets, bank hash and signed/unsigned payload checks accompany each package. |
| Physical phone | NOT TESTED | Actual install/update, WebView lifecycle/storage, Android system bars, keyboard and accessibility require device confirmation. |
| Production service | NOT DEPLOYED | Persistent SQLite and HTTPS configuration is supplied. Live production TLS, reverse proxy, backup restoration, capacity and classroom load remain untested. Community Cloud alone is not the durable data service. |
| Faculty readiness interpretation | NOT ESTABLISHED | Independent content review, complete PRC coverage and predictive validation remain pending. No score certifies board readiness. |

A follow-up upgrade regression reproduced v0.8.0 rejecting a stored older bank when 20 genuinely new shipped items were added. v0.8.1 passes exact bundled content as the trust baseline while retaining all old grading content and rejecting unknown unapproved imports. Public and actual private migration checks preserve history, a 50-item queue and an unfinished session. The old data was never erased. Use v0.8.1 for updates.

Snapshots are private owner backups, separate from server grading. Voluntary faculty reports are device-recorded summaries, not audit/proctoring evidence. Conflict recovery is explicit; no automatic overwrite is attempted across devices. No application feature can establish the cause of an examination failure from usage or score data alone.

Export progress and bank before updating over a same-certificate candidate. Preserve the prior APK and matching backups for rollback; lower-version Android installation is normally blocked. Preserve server bank_versions and SQLite backups before an API/bank upgrade. See ONLINE_SYNC.md and BOARD_READINESS.md for acceptance procedures and limits.
