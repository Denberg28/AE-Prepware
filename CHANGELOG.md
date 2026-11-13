# Changelog

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
