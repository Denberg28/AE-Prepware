# AE Prepware v0.3.0-rc.1 · Signed test candidate

AI/IN source controls, faculty admin corrections and safe bank refreshes.

- Tick AI, IN or both before choosing a subject: 50 from one source or 25+25 Hybrid.
- Show AI/IN origin in each question; block insufficient pools without duplicates.
- Separate server-side admin sign-in for text, choices, key and explanation edits.
- Append reviewed corrections; retain original IDs/keys for old scores and sessions.
- Import compatible reviewed updates without resetting progress or queued results.
- Archive API bank versions so older queued results retain their original grade.
- Instructor JSON provenance/approval/duplicate validation and dedicated upload folder.

The bundle contains 360 AI foundation items, 60 per subject. IN pools start empty;
no missing/reported 2,005-question corpus is represented as delivered. Reviewed
instructor JSON can enable IN and Hybrid per subject. No commercial source PDF is
redistributed. Admin editing needs AE_ADMIN_USERNAME and AE_ADMIN_PASSWORD_HASH
in Streamlit Secrets; see docs/ADMIN.md. The service is not newly deployed.

Update over permanent-signer v0.2 without uninstalling; export progress and any
custom bank first. Package identity remains ph.diversify.aeprepware; versionCode 3.
The certificate is unchanged. Physical Android installation, in-place upgrade,
SAF, accessibility, live hosting/AI and independent faculty validation remain
untested. This is a test candidate, not a stable release or pass guarantee.

Retain v0.2 and its matching progress/bank backup for rollback. Android blocks
lower-version installs; uninstalling deletes local data. Do not import a new-bank
backup into an old APK. Preserve server SQLite bank_versions archives.
