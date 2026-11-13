# AE Prepware v0.2.0-rc.1 — signed test candidate

Simplified Android UI: choose a subject, answer 50 distinct randomized bank questions, receive immediate correct/incorrect letter feedback, and expand explanations only when needed. Final score and answer review are saved in Results.

Adds offline account creation with account number/recovery code, separate local profiles, resumable study and account-bound results. Optional HTTPS API sync regrades results, deduplicates retries and backs up progress for recovery on another device. Ranking uses daily unique-correct points. Random/adaptive selection works offline; optional Gemini-assisted topic selection uses synced account progress and cannot change bank answers.

Bank expanded from 72 to 360 original foundation items, including parameterized calculation exercises; 60 per subject. Existing 72 IDs/keys preserved. Faculty review and full TOS coverage remain pending. Optional Streamlit faculty dashboard and Secrets setup remain supported.

## Install / update

Android 8+ and current System WebView. Package ph.diversify.aeprepware, versionCode 2. This APK is non-debuggable and uses the permanent AE Prepware release certificate. Public certificate, fingerprint, source/build verification, checksum and manifest are attached. Private signing key is not public.

**From v0.1 only: export your progress backup BEFORE uninstalling.** The previous CI debug signing key is unavailable, so this first permanent-signer version requires a one-time uninstall/reinstall. Install v0.2, restore the old guest backup, then create an account. Later versions can update with the same permanent certificate and increasing versionCode. Back up before updates or downgrades; app uninstall deletes local data.

## Verification and limits

Automated core/account/API tests, mobile browser study flow, real local API/SQLite integration (including dropped sync acknowledgement and another-device recovery), Android debug/release build/lint, dependency audit and APK signature/source-payload checks are required before publication. Evidence is under docs/evidence/V0_2_VERIFICATION.md and CI artifacts.

No physical phone testing, production HTTPS deployment, real Gemini provider call or independent faculty content approval is claimed. Accounts work offline, but shared ranking/cloud recovery requires an operator-hosted service; no default hosted endpoint is embedded. Streamlit hosts only faculty UI. These are practice results, not official/proctored rankings or a guarantee of passing. Candidate only, no stable promotion.

Rollback requires an APK and bank/progress backup compatible with that version. Android blocks lower versionCode and mismatched certificates; export before uninstalling. Never overwrite a published version or change the permanent signing key for normal updates.
