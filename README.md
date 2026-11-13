# AE Prepware

**PRC-focused study update:** default 20-question PRC foundations drills use a curated 120-item AI set (240 AI/IN items in the private build). Full bank retains 50-question practice. This is an incomplete starter core, with advanced coverage gaps shown in Settings. Read the [2022–2026 evidence and bank review](docs/PRC_2022_2026_REVIEW.md) before interpreting coverage.

Core development principle: **commitment, competence, readiness**. Every feature should build a sustainable study habit, improve demonstrated understanding, or make remaining subject gaps visible. Recorded app use is a participation measure, not proof of motivation.

Minimal Android practice for Philippine Aeronautical Engineers Licensure Examination subjects. **v0.8.1-rc.1 is a test candidate**, pending physical Android testing and independent faculty content review.

## Commitment · Competence · Readiness

Open **Results** to track recorded participation, first-attempt and diagnostic evidence, and subject support priorities. New-item diagnostics and seven-day spaced rechecks reveal results after submission. Readiness stays unestablished while PRC coverage and validation are incomplete. Export a voluntary alias-based report for the private faculty dashboard's **Board readiness** tab. Goals, first observations and initial diagnostics are included in progress backups; full Sync now backs up this journal and unfinished checks. See [workflow and interpretation rules](docs/BOARD_READINESS.md).

## Sync and feedback practice

The **upper-right circular-arrow button** uploads server-graded results and a private profile backup, refreshes practice ranking and checks the compatible question database. Offline work remains available. Account settings separately opt in to ranking and facilitator summaries. Interrupted uploads retry without duplicate scores; a newer backup on another device produces a recoverable conflict.

A one-tap **Bearing · Heading · Throat** drill supplies 20 original AI-labeled, source/formula/arithmetic self-checked exercises, with worked explanations: six bearing, six heading and eight nozzle/throat calculations. Independent faculty review remains pending. The 120-item public / 240-item private foundations core stays compact; the full AI bank now has 380 records. Old questions and keys are retained.

See [online setup](docs/ONLINE_SYNC.md) for the persistent API plus Streamlit dashboard, including a single-host runner and Dockerfile. Streamlit Community Cloud alone is still not the durable sync database. No production host has been provisioned.

## Appearance and subject weights

Use the moon/sun button at the upper right to switch light/dark. The device-wide
choice is saved separately from accounts and progress. Android system bars follow
the selected theme. Subject cards show PRC exam weights; Settings lists the full
breakdown and official November 2026 examination-program source. Both app bars
remain stationary, and only the center pane scrolls.

## Study

1. Choose **PRC foundations** (20 questions) or **Full bank** (50), tick **AI**, **IN**, or both, then choose a subject. Hybrid draws 10 or 25 from each source respectively. Questions and their original three/four choices are shuffled; insufficient pools are disabled. AI labels AI-produced questions; IN labels instructor uploads.
2. Select a letter. The answer locks, shows **Correct** or the correct letter/text, and offers a collapsed **Explanation** pane.
3. Finish the selected 20 or 50 to see your score. **Results** records sessions and subject progress. Save & exit/reopening resumes exactly.

The public snapshot preserves 360 original AI foundation records (60 per subject), including parameter variants. Its default core selects 120; context-dependent ST005 is retired. Advanced TOS coverage is incomplete. Answer keys and source explanations are fixed; live AI cannot change them. Imported banks need approval metadata or the documented private source-key-verification provenance. Quotas require distinct, active, non-set-aside items.

The 360 bundled items are explicitly labeled **AI**. No recovered IN corpus is included: IN-only and Hybrid become available per subject after reviewed instructor JSON is imported. The attached guides were subsequently processed for a separate private study build: 2,003 text-only IN questions were matched to printed keys; 67 figure/ambiguous items were held. Those book contents are not in the public repository/APK. [Private guide workflow](docs/PRIVATE_GUIDES.md). See [instructor uploads](instructor_uploads/README.md).

Faculty admins can correct text, choices, keys and explanations after a separate server-side sign-in. Corrections append reviewed revisions and retain old questions for saved scores and pending results. Compatible bank refreshes preserve Android progress and unfinished sessions; the API archives original keys across restarts. [Admin setup and editing](docs/ADMIN.md) describes configuration, exports and recovery. Keep server Secrets private; there is no default admin password.

Offline use needs no server, AI key or payment. Adaptive selection is the new-profile default and favors unseen/missed/due questions. Core selection spreads questions across available topics. Existing selection preferences are preserved. **AI assisted** uses a connected account's synced performance to request topic priorities; without a provider or service it falls back to adaptive selection, labeled in the UI.

## Accounts, saved results and ranking

Create an account in **Account**. The app issues an **AE- account number** and a private recovery code. Save the recovery file and a separate progress backup. Account number alone cannot sign in. Guest progress can be bound to the first new account; different profiles have separate storage. Up to ten local profiles are supported. Recovery codes are verified by digest locally and salted scrypt on the service; the app does not retain their plaintext after creation. Anyone using an unlocked, signed-in phone can view that profile; profiles are not a device encryption boundary.

An account works offline first. For online backup/ranking, use the instructor's **HTTPS API root URL**, enter the recovery code and select **Connect account**. Completed 20- or 50-item sessions queue locally and are graded again by the server. Lost responses and retries do not double-count results or points. Sync retains queued sessions on failures. The pending queue caps at 200; sync/export before more sessions. Latest 200 summaries are shown locally and in cloud recovery; server aggregate progress retains all synced attempts.

Shared ranking awards one point per distinct correct question per server day (Asia/Manila). Public ranking shows a display name and masked account suffix. These are self-paced practice standings, not verified identities or proctored exam scores: offline answer keys are inspectable. The service is not deployed by this repository. New-device sign-in restores synced results/progress; unsynced work needs a progress backup; Full Sync additionally protects flags, bookmarks and the monitoring journal. Lost recovery codes cannot be reset by account number. Server login tokens expire after 30 days; reconnect with the code. Device signout clears its token; online deletion permanently removes server records, while local scores remain.

## Install and update

Download the signed candidate from [GitHub Releases](https://github.com/Denberg28/AE-Prepware/releases). Android 8+ and a current Android System WebView are required. Allow APK installation from your browser/file manager.

**One-time transition from v0.1:** export progress in the old app first. That CI build used a disposable debug certificate whose private key is unavailable. Uninstall it, install v0.2, then import the old guest backup and create your account. Original question IDs and progress/session schema remain compatible. Never uninstall without backup. Subsequent versions use the permanent certificate and a higher versionCode so normal updates can preserve app data. A signing certificate does not imply educational validation or a stable release.

The public certificate, fingerprint, SHA-256 checksums and verification report accompany the APK. See [signing and release procedure](signing/README.md). Private signing recovery material is never public. To roll back, export a matching progress/bank backup first; Android blocks lower-version installs without uninstall, and backups tied to expanded banks may not load in older apps. Keep the older APK and its matching backup.

## Build and test

Android: JDK 17/21, Gradle 8.10.2 wrapper, SDK platform 35/build-tools 35.0.0. Minimum API 26, target 35; no Android third-party runtime dependencies. `release.json` controls version/code and pinned certificate. Local debug APKs are for development; publication uses the permanent signed release.

```sh
./gradlew :app:assembleDebug :app:assembleRelease :app:lint
node --test tests/*.test.cjs
python -m venv .venv
. .venv/bin/activate # Windows: .venv\Scripts\activate
pip install -r backend/requirements.lock -r scripts/requirements-authoring.lock
python -m pytest -q
npm ci
npx playwright install chromium
mkdir -p artifacts
node tests/browser.cjs
node tests/cohort-browser.cjs
node tests/sources-browser.cjs
node tests/private-bank-browser.cjs
node tests/shell-browser.cjs
node tests/theme-browser.cjs
```

The integration browser test uses real local API/SQLite, simulated HTTPS origin and separate storage contexts; it is not a physical-phone or live TLS test. `CHROMIUM_PATH` selects a system Chromium. See [test gates](docs/TESTING.md) and [v0.8 evidence](docs/evidence/V0_8_VERIFICATION.md).

## Hosted account API

```sh
# From repo root, Python virtual environment, one worker
# AE_DB=/persistent/path/cohort.sqlite
# AE_BANK=/path/to/approved-bank.json # optional, exact same bank on phones
# GEMINI_API_KEY=server-only-key     # optional AI topic selection
# GEMINI_MODEL=gemini-3.5-flash-lite # optional model override
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --workers 1
```

Use persistent disk, private database backups and a valid HTTPS reverse proxy with request/connection limits. No API key is embedded in Android. AI receives only topic names and aggregate attempts/correct counts, not account identifiers, names, recovery codes or student records. Configure provider quotas separately. It can select only allowlisted topics; malformed/provider failures use adaptive selection and cannot change bank keys. Streamlit Community Cloud hosts the faculty UI below; it does **not** host this FastAPI service or automatically pass its Secrets to a separately hosted API. Legacy v0.1 cohort endpoints remain available for compatibility; new account rankings are separate.

## Streamlit faculty dashboard

Run `python -m streamlit run streamlit_app.py`. For Community Cloud:

| Field | Value |
| --- | --- |
| Repository | `Denberg28/AE-Prepware` |
| Branch | `main` |
| Main file path | `streamlit_app.py` |
| Python | `3.12` |

In **Advanced settings → Secrets** (or existing **App settings → Secrets**) use top-level TOML:

```toml
GEMINI_API_KEY = "paste-your-gemini-api-key-here"
GEMINI_MODEL = "gemini-3.5-flash-lite"
# Optional separately hosted service:
# AE_API_URL = "https://your-cohort-api.example.com"
```

Restrict dashboard sharing to instructors. Anyone with access can trigger server API usage. The root `requirements.txt` installs the minimal dashboard runtime. Streamlit Secrets take priority over environment variables. For local use, copy `.streamlit/secrets.toml.example` to ignored `.streamlit/secrets.toml`. The old `backend/dashboard.py` entry remains supported. Draft coursework always requires instructor review, and the dashboard never inserts live drafts into the scored bank. Export review work before reboots.

## Content and limitations

Edit original content in `scripts/generate_bank.py` and `scripts/expand_foundations.py`; regenerate with `python scripts/generate_bank.py`. Preserve IDs/keys for unchanged items; changes to identity/key require versioning and progress migration review. All independent faculty approvals require individual checks and a new bank version. No copied commercial Prepware/Quizlet items or recalled exams.

See [scope](docs/V0_2_SCOPE.md), [architecture](docs/ARCHITECTURE.md), [content policy](docs/CONTENT.md), [known limitations](docs/KNOWN_ISSUES.md), [changelog](CHANGELOG.md) and [release notes](docs/RELEASE_NOTES.md).
