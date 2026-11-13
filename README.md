# AE Prepware ✈

A lightweight Android study companion for Philippine Aeronautical Engineers Licensure Examination preparation. Offline multiple-choice practice, explanations, progress, adaptive quests and optional cohort challenges. **v0.1.0-rc.1 is a test candidate, not a stable or comprehensive board reviewer.**

## Install and study

Download the candidate APK from [Releases](https://github.com/Denberg28/AE-Prepware/releases). Android 8.0+ and a current Android System WebView are required. Allow installation from your browser/file manager, install the APK, then open AE Prepware. No account, ad service or AI key is required for offline study.

- **Today:** start recommended practice or resume your saved question.
- **Study:** subject sessions, shuffled practice, mistakes, bookmarks and a 20-item weighted check.
- **Progress:** question coverage, practice accuracy, correct-answer streak milestones and session log.
- **Cohort:** optionally join an instructor-provided HTTPS service with a pseudonym. Submit server-scored challenges and view standings.
- **Settings (•••):** name, JSON backup/restore, approved question-bank import and disputed-question reports.

72 original foundation questions include explanations and references. They cover all six subject headings and use PRC November 2026 weights; they do **not** cover every syllabus/TOS competency. The bundled bank has author self-review; independent faculty review is pending. No copied commercial Prepware/Quizlet content, recalled exam questions, PRC affiliation or guaranteed passing result. Review corrections with qualified faculty before relying on the material.

## Reproducible setup

Android: JDK 17 or 21, Gradle wrapper 8.10.2 (checksum pinned), Android SDK platform 35 and build tools 35.0.0; minimum API 26, target 35. Android has no third-party runtime dependencies.

```sh
# ANDROID_HOME points to your SDK; alternatively create ignored local.properties
./gradlew :app:assembleDebug :app:assembleRelease :app:lint
node --test tests/*.test.cjs
```

Debug APK: `app/build/outputs/apk/debug/app-debug.apk`. Release build is unsigned until the maintainer provides a private signing key. The candidate distributed by CI is explicitly debug-signed. Never commit a keystore. A future production signer must be provisioned before stable distribution; export a backup before switching signing identity because uninstall may be necessary.

Python 3.12 recommended. Use a virtual environment:

```sh
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r backend/requirements.lock
python -m pytest -q
python -m streamlit run streamlit_app.py --server.address 127.0.0.1
```

The Streamlit dashboard provides a template coursework plan, optional Gemini AI drafts and per-question faculty approval/export. It can run locally or on Streamlit Community Cloud. No deployed dashboard or paid hosting is assumed. Review work is preserved by exporting JSON, not by relying on the Streamlit session.

### Streamlit Community Cloud setup

Create an app with these entries:

| Field | Value |
| --- | --- |
| Repository | `Denberg28/AE-Prepware` |
| Branch | `main` |
| Main file path | `streamlit_app.py` |
| Python version (Advanced settings) | `3.12` |

Paste the following **top-level TOML entries** into **Advanced settings → Secrets** before deployment, or **App settings → Secrets** for an existing app:

```toml
GEMINI_API_KEY = "paste-your-gemini-api-key-here"
GEMINI_MODEL = "gemini-3.5-flash-lite"
# Optional, separately hosted cohort service:
# AE_API_URL = "https://your-cohort-api.example.com"
```

Only the API key is required for AI; omit `GEMINI_MODEL` to use the shown default, or choose a model available to your account. Save Secrets and rerun the app. In **Coursework → Optional AI draft assistant**, click **Draft a coursework plan with AI**. Configuration status means settings were loaded, not that the provider accepted the key. Invalid keys, quota limits and network errors show a generic error; local coursework still works. Live generation remains untested without a real key.

Settings are read from `st.secrets` first, then server environment variables. For local use, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and edit the ignored copy. Never put a real key in source, the example file, Android, or a student input field. Root `requirements.txt` installs just the dashboard runtime; `backend/requirements.lock` retains the full development/API environment. The older `backend/dashboard.py` entry also remains supported.

Restrict app sharing to intended instructors in Streamlit Cloud; on other hosting, use an authentication gateway. Anyone with dashboard access can trigger API usage with the server key. Streamlit hosts this faculty UI, not the separate cohort API. Keep the Android app offline-first. Export review work before app reboots or upgrades. To roll back this setup, use the previous commit's `backend/dashboard.py` entry and environment settings; no Android data migration is involved.

Optional cohort API:

```sh
# From the repository root, in the virtual environment
# AE_DB=/persistent/path/cohort.sqlite
# AE_BANK=/path/to/faculty-approved-bank.json  # optional; same version on phones
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --workers 1
```

Put the API behind a valid HTTPS reverse proxy with request limits and persistent disk. Give students the HTTPS root URL. Android rejects cleartext HTTP. Cohort hosting is not included in the APK and has not been deployed. Local study remains available without it. See [architecture](docs/ARCHITECTURE.md) for account/privacy and hosting limits.

Browser regression test (desktop simulation of local UI, not Android validation):

```sh
npm ci
npx playwright install chromium
node tests/browser.cjs
```

The browser test starts its own static server on port 8080. Set `CHROMIUM_PATH` when using a system Chromium. Screenshots/evidence go to ignored `artifacts/`.

## Content maintenance

Edit `scripts/generate_bank.py`, then `python scripts/generate_bank.py`. The bundled bank is source-checked by its initial author, not automatically faculty-approved. The dashboard can review a bank one question at a time and export an entirely approved bank with a new version. Android only accepts imported banks marked approved for **all** questions. Review metadata is not a cryptographic signature; obtain banks only from trusted instructors.

Backups require the same bank version. Changing banks resets progress after confirmation; export a progress backup and preserve the matching old bank first. Unsupported/corrupt data is rejected and retained for recovery. Setting aside a disputed question excludes it from future local practice; export reports for faculty review.

## Delivery and rollback

GitHub CI runs bank/core/API tests, browser regression, dependency audit, Android assemble/lint and APK packaging checks. The initial main build (or its matching version tag) publishes a **prerelease** only after required CI checks. Bump the version before publishing another artifact; existing releases are never overwritten. CI uploads the tested candidate APK, checksums, source identity and reports. No stable promotion is automatic. Candidate signer changes between clean CI builds; use backup/uninstall/reinstall if Android rejects an upgrade. This is deliberate candidate-only signing, not production continuity.

There is no earlier baseline release. To roll back after later updates, keep a matching bank/progress backup, uninstall only after export, reinstall the earlier compatible APK and restore that backup. Schema downgrade across incompatible banks is unsupported.

See [specification](docs/SPEC.md), [test gates and device procedure](docs/TESTING.md), [known limitations](docs/KNOWN_ISSUES.md), [content policy](docs/CONTENT.md), and [changelog](CHANGELOG.md).
