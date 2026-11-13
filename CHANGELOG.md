# Changelog

## 0.8.2-rc.1 — 2026-11-14

- Restore the previous simple Subjects screen by removing the commitment/competence/readiness banner and separate bearing/heading/throat shortcut. Retain Sync, theme, fixed app bars and subject weight badges.
- Integrate all 20 calculation exercises into the normal Aerodynamics foundations pool. Existing foundation questions remain available; 20-question sessions draw from a 40-item AI Aerodynamics core. Full-bank question IDs and keys are unchanged.

## 0.8.1-rc.1 — 2026-11-14

- Fix automatic upgrade of a stored v0.6 bank when the new bundled bank adds source-checked exercises. Trust only exact shipped content while retaining immutable old keys and requiring approval for unknown imports.
- Strengthen the migration browser test with genuinely new bundled records; preserve saved scores, queued results and an unfinished session.
- Supersede v0.8.0-rc.1 for stored-bank upgrades; blocked old data remains recoverable and is not erased.

## 0.8.0-rc.1 — 2026-11-14

- Establish commitment, competence and readiness as the product principle and home entry point.
- Add upper-right full Sync: idempotent private backups, recovery of the monitoring journal and unfinished checks, opt-in practice ranking and facilitator sharing, and authenticated compatible bank pulls.
- Add persistent SQLite snapshot revisions/conflict detection, enrollment-gated private bank downloads, protected faculty summary retrieval and a combined Streamlit/API host.
- Append 20 original source-checked bearing/heading/throat exercises with independent numerical tests and a one-tap drill; retain all old question keys and the compact core.

- Add offline Board Readiness Monitoring under Results: activity goals, first-attempt observations, retained initial diagnostics, recent competence evidence and subject priorities.
- Add 20-item new-item diagnostics and seven-day spaced rechecks with deferred feedback, restart persistence and exact once-only grading.
- Keep PRC-weighted foundation scores incomplete until all six subjects have recent evidence; separate foundation targets from unestablished board readiness and content gaps.
- Add voluntary alias-based facilitator JSON exports and an admin-gated faculty report importer/CSV, with per-file validation, freshness, duplicate handling and spreadsheet-injection protection.
- Preserve old question IDs/keys, scores, normal practice, source quotas, accounts, themes and signing identity.

## 0.6.0-rc.1 — 2026-11-14

- Review official 2022–2026 programs and the detailed PRC TOS; record sources, selection policy and coverage gaps.
- Add a 120-item public AI foundation core and a separately distributed 240-item private AI/IN core; retain the complete reference bank and immutable historical keys.
- Add 20-question topic-diverse core drills and matching 10+10 Hybrid, alongside full-bank 50/25+25 practice.
- Support server grading, recovery and idempotent sync for both 20- and 50-item account results.
- Refresh directly compatible stored banks after question and saved-state validation.
- Correct selected private subject assignments through 34 append-only copies; retire five questionable IN items and context-dependent ST005 without changing old keys.
- Show explicit coverage gaps; independently recalculate 264 parameterized AI exercises and 77 selected numeric exercises. Faculty and device validation remain pending.

## 0.5.0-rc.1 — 2026-11-13

- Restore PRC subject-weight badges and the linked Settings breakdown, verified against the official November 2026 PRC program.
- Add a remembered sun/moon theme toggle at the upper right; use matching Android status/navigation bar colors and icon contrast.
- Refine subject cards, bank selectors, controls and feedback with shared light/dark design tokens and accessible contrast.
- Apply theme before page styling, prevent low-contrast crossfades and preserve question order/answers when toggling.
- Keep fixed chrome, center-only scrolling, signing identity and all private IN data unchanged.

## 0.4.1-rc.1 — 2026-11-13

- Keep header/navigation stationary; only the center pane scrolls on all screens.
- Remove the subject heading and repeated instructions; use compact source/session status and source counts. Move review detail into Explanation/Settings.
- Consolidate styles, standardize readable question/choice fonts and spacing, and keep navigation accessible during a quiz.
- Verify center-only scrolling, steady bars, next/tab scroll reset, long questions, enlarged text and saved-session continuity.
- Retain the private 2,003-item IN bank, original keys, account/progress formats and signing identity.

## 0.4.0-rc.1 — 2026-11-13

- Inset a native parent around WebView so the header and fixed navigation stay clear of Android system bars. Compact header/content/checkbox spacing and improve label contrast.
- Preserve original three-choice IN questions alongside four-choice questions; grade and restore mixed sessions correctly.
- Persist large imported banks in IndexedDB with legacy bank support and bank export; raise JSON file limit to 8 MB.
- Add a private PDF importer, source-key review status, figure/ambiguous hold queue, private asset build overlay and a public-publication guard.
- Separately deliver 2,003 private IN items from the supplied guides; 67 held for manual review. Book content is excluded from public git/APKs.

## Unreleased · faculty dashboard compatibility

- Preserve the existing private admin number/recovery bootstrap alongside username/password-hash login. Android APK bytes are unchanged.

## 0.3.0-rc.1 — 2026-11-13

- Label the bundled foundation bank AI and show AI/IN origin in questions. Add source checkboxes: 50 AI, 50 IN, or 25+25 Hybrid; disable insufficient pools.
- Add separate server-side faculty admin sign-in, reviewed text/choice/key/explanation revisions and validated instructor JSON import/export. No default admin password.
- Keep old IDs and keys for historic/queued sessions; compatible Android refreshes preserve progress. Archive API bank versions for grading after updates and reject changed archived IDs.
- Add instructor_uploads contract/merge CLI, duplicate and provenance checks, admin and mobile refresh regression tests.
- No recovered IN corpus is bundled. Physical Android update/SAF/accessibility and independent faculty review remain pending; candidate tier only.

## 0.2.0-rc.1 — 2026-11-13

Minimal subject-first UI with 50 distinct questions, shuffled letters, immediate locked feedback, collapsed explanations and recorded final scores. 360 original foundation items (60/subject, including parameter variants), preserving the original 72 IDs/keys. Offline recoverable account numbers with isolated profiles; optional server-graded result sync, retry-safe queues, account recovery/progress/ranking, adaptive selection and bounded Gemini topic selection. Streamlit Secrets setup preserved. Permanent non-debug release signer, public certificate, private recovery backup and CI verification of prepared signed APKs against rebuilt source payloads. One-time backup/reinstall from v0.1 required because its disposable CI signer is unavailable. Android device, live hosting/AI and faculty review remain pending.

## 0.1.0-rc.1 — 2026-11-13

Initial Android test candidate: offline original 72-question foundation bank; immediate explanations and source links; shuffled subject/adaptive practice; mistake and bookmark review; weighted short checks; durable on-device progress/session resume, daily quests and XP; JSON backup/recovery; question set-aside reports; optional server-scored cohort ranking with hashed anonymous credentials, retry-safe submission and account deletion; private Streamlit coursework/faculty review dashboard; optional server-side Gemini coursework drafts; CI and device-validation procedure.

Independent faculty bank review, physical Android validation, live AI-provider validation and production HTTPS cohort hosting remain outstanding. No stable release claim.
