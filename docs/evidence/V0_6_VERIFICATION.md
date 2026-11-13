# v0.6.0-rc.1 verification — 14 November 2026

Baseline: public v0.5.0-rc.1 / commit 2b6ae01852877c85800d25f676bf2edd1f478cf0. The update addresses PRC-focused bank size, relevance and learning efficiency. It is a test candidate, not a stable or faculty-approved release.

| Gate | Result | Evidence |
| --- | --- | --- |
| Content integrity | PASS | Public 360 records preserved; 120 core IDs; 264 parameterized calculations recomputed from printed givens and 77 selected numeric exercises checked against independent values. |
| Private integrity | PASS | All 2,363 old records retain grading content; 34 subject-correction copies match originals; 240 core IDs; five semantic-review retirements plus ST005. Original 2,003 source-key matches inherited, not independently re-approved. |
| Node unit checks | PASS | 28 checks: core map/quotas/diversity, 20/50 queues and legacy behavior alongside existing grading/state/source tests. |
| Python/API checks | PASS | 31 checks: core curation/recalculation, exact 20/50 grading, idempotent retries, 10+10 three-choice Hybrid, forbidden fabricated D, old bank archives and authoring behavior. |
| Browser workflows | PASS | Seven public/synthetic workflows plus actual private-bank run: study/account recovery, source refresh, private persistence, steady chrome, theme/contrast, core migration and local API lost-ack retry. |
| Android | PASS | Debug/release assemble and lint, SDK/build-tools 35, Gradle 8.10.2, JDK 21. |
| Dependency audits | PASS | npm and both pinned Python lockfiles have no reported vulnerabilities. |
| Signed packages | Separate manifests | Permanent signer and package identity; versionCode 7; source marker, all assets, bank hash and signed/unsigned payload comparison. |
| Physical phone | NOT TESTED | Real install/upgrade, WebView storage/keyboard, scrolling, native bar colors and accessibility need device validation. |
| Faculty and current jurisdiction | PENDING | Source-checked foundations and historical guide keys do not establish comprehensive PRC coverage or current Philippine legal validity. |

The detailed official-source review, precise coverage gaps and the practical limits of a 240-item starter set are in `docs/PRC_2022_2026_REVIEW.md`. No actual five-year PRC paper corpus or recurrence statistics were established. No unreviewed AI questions were added to scored practice. Guide content remains private.

The focus migration test preserves an old 50-item queue and unfinished session, upgrades a stored bank only through its declared compatible parent, completes a new 20-item account session, and verifies Full bank remains available. API tests reject unsupported lengths, repeated IDs, mixed subjects and nonexistent choice D. Account API plans default to Full for older clients. The pytest collection database is isolated so tests do not touch a developer's study database.

Use the signed candidate over v0.2–v0.5 after exporting bank/progress. A lower-version Android install is blocked; do not uninstall without matching backups. No hosted API deployment is included. Keep archived server banks for old queued results.
