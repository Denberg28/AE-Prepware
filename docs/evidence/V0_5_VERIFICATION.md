# v0.5.0-rc.1 verification · 2026-11-13

Baseline e6073b7 / signed v0.4.1. User requested PRC percentages, professional
minimal controls and a sun/moon appearance toggle. Source weights were verified
against pages 1–2 of the official November 2026 PRC program (Settings source link).
The bank weights/IDs/keys and private 2,003 IN items remain unchanged.

| Gate | Status | Evidence |
| --- | --- | --- |
| A/B/C core/API | PASS | Existing 24 Node + 28 Python tests: grading, accounts, queues, source provenance and storage |
| B/C appearance/browser | PASS | Exact six badges/100% total, light/dark enabled/disabled text contrast, sun/moon action/placement, persistence/native messages, quiz-state integrity, fixed chrome across widths, storage-failure recovery |
| B/C regression browser | PASS | Study, source refresh, private-bank upgrade retention, shell scrolling and actual local API recovery/retry workflows |
| A Android | PASS | Debug/release assemble and lint with SDK/build-tools 35, Gradle 8.10.2, JDK 21; guarded native theme/system-bar APIs |
| F packages | See manifests/verification reports | Unchanged signer/package, versionCode 6, source/asset/checksum/full unsigned-payload verification; private content not publicly published |
| Real phone appearance/install | NOT TESTED on this revision | Native icon pixels, bar colors, keyboard/resume/cold-start and real upgrade/accessibility need phone confirmation |
| Faculty approval | BLOCKED | Existing source-key agreement does not imply independent faculty review |

Self-reviewed candidate evidence only. Appearance is a device-wide enum preference,
separate from accounts/progress; invalid stored values default to light. Early
external theme script applies before CSS to avoid a saved-theme light flash.
Instant palette changes avoid a low-contrast background/text crossfade. JavaScript
passes only light/dark to the guarded native bridge; native preferences, root
padding background and system icon appearance are updated without WebView reload.
WebView algorithmic darkening is disabled so explicit colors are not transformed.
No scored questions, answer keys or session orders change during a theme switch.
