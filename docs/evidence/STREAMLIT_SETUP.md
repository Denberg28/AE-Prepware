# Streamlit Cloud setup verification — 2026-11-13

Scope: source update from baseline `697ddc5`; root Cloud entry, dashboard configuration and deployment documentation. Existing Android candidate/tag remains the baseline artifact. No new APK release or stable promotion is requested by this change.

Acceptance: Cloud can select a root entry with discoverable runtime dependencies; top-level Secrets supply the server API key; absent credentials preserve local coursework; configured credentials enable a draft request; provider failures preserve the UI and do not publish content or expose the key.

| Check | Status | Evidence |
| --- | --- | --- |
| Python/API/dashboard regression | PASS | `python -m pytest -q`: 11 tests; 4 dashboard tests use Streamlit AppTest and mocked provider requests. Root entry, three tabs, missing-secret file/environment fallback, Secrets precedence, default and custom model, key non-display, successful draft and HTTP 429 recovery checked. |
| Offline quiz/core regression | PASS | `node --test tests/*.test.cjs`: 12 tests. |
| Android build/lint regression | PASS | Cached Gradle 8.10.2 binary, JDK 21, SDK 35: offline assembleDebug, assembleRelease and lint succeeded. Wrapper bootstrap initially blocked by network; direct installed distribution used. |
| Configuration | PASS | Example parses as TOML; real `.streamlit/secrets.toml` is git-ignored; root runtime versions match the existing environment; `pip check` passes. |
| Source self-review | PASS | Only example credentials tracked; real key never rendered or included in APK; existing backend entry retained. |
| Live Streamlit Cloud deployment | NOT TESTED | Entry and dependencies prepared for deployment; no hosted URL claimed. |
| Live Gemini request | BLOCKED | No real provider API key supplied. Automated provider requests are simulated. |
| Android physical validation/content review | BLOCKED | Existing candidate limitations unchanged; this update changes no Android runtime source or question bank. |

Root runtime: Python 3.12 recommended, Streamlit 1.67.0, httpx 0.28.1. Copy deployment values and secret template from README. Rollback: select the baseline commit and `backend/dashboard.py` entry with environment settings. Export faculty review work before rebooting; no schema migration applies.
