# Offline individual data → online Streamlit

AE Prepware's product principle is **commitment, competence, readiness**. Full Sync protects each student's local work and makes voluntary summaries available for facilitator support.

## Student workflow

1. Create an offline account and save its recovery file.
2. In Account, enter the instructor's **HTTPS root service URL**, recovery code and enrollment code if required. Connect once.
3. Ranking and facilitator sharing are separate, unchecked choices. Enable only the desired choices, then press the upper-right **Sync** icon.
4. Sync grades pending results on the server, updates ranking consent, backs up the profile, refreshes standings and checks the question database. An interruption preserves the queue. Results already accepted are not counted twice.
5. On another device with the matching bank, sign in with the same number/code/service. Recovery restores the monitoring journal, goals, flags, bookmarks and unfinished check from the snapshot, then merges any newer server-graded results. It does not restore unsynced work from another phone.

A full sync is a sequence of independently saved steps, not a single database transaction across devices. Account shows the last attempt and completed steps. A failed later step does not undo earlier accepted results or delete local work. A stale revision cannot overwrite a newer snapshot. Export a local progress backup, then use **Restore online backup** to explicitly resolve the conflict; check the two devices before choosing which unfinished work to keep. Reset queued backup upload only discards that transport copy, not study progress.

## Hosting choices

**Streamlit Community Cloud:** keep entry `streamlit_app.py`. It hosts the faculty UI, which reads the persistent API configured through `AE_API_URL`. Add the same private `AE_FACULTY_SYNC_KEY` to both services for the admin-gated **Sync online readiness summaries** action. Cloud's local/session filesystem is not the durable student database. This repository has not provisioned a production host.

**One persistent host:** `online.py` serves the API at the root and Streamlit at `/dashboard/` using Streamlit's ASGI application support. Run one worker, behind HTTPS, with a persistent writable disk:

```sh
pip install -r backend/requirements.lock
export AE_DB=/persistent/ae-prepware.sqlite
export AE_API_URL=https://your-school-service.example
export AE_FACULTY_SYNC_KEY=your-random-server-only-key-at-least-32-characters
export AE_ADMIN_USERNAME=your-faculty-admin
# Generate AE_ADMIN_PASSWORD_HASH using scripts/admin_password.py; keep it private.
uvicorn online:app --host 127.0.0.1 --port 8501 --workers 1
```

The API root supplied to Android must be the HTTPS origin, without `/dashboard` or a query string. A reverse proxy must forward WebSockets and permit 1 MB snapshot requests. The existing app sends requests only to its configured HTTPS service; localhost HTTP is used only in automated tests. The Dockerfile exposes port 8501 and expects a persistent volume mounted at `/data`. Supply secrets at runtime; never bake them into the image. Python 3.12, locked dependencies, and one SQLite worker are supported. A production TLS, backup/restore and concurrency test remains necessary before classroom deployment.

## Bank and private content

- By default, serve the committed original AI bank. Use `AE_BANK` to select the matching reviewed private bank on an instructor-controlled host; the private JSON is supplied separately and is never committed or put in the public image.
- Private bank downloads default to disabled. To enable them, set `AE_ALLOW_PRIVATE_BANK_SYNC=true` and a private `AE_ENROLLMENT_CODE` of at least 16 characters. Students must connect with that code to become enrolled. Merely knowing an account number or creating an account before downloads were enabled cannot grant download access. Legacy public challenge routes are disabled on a private bank host.
- An unchanged version must have exactly unchanged bytes/content. A refresh must extend the installed version, preserve all previous question grading content, and meet the existing approval rules. Incompatible updates stay unapplied; no automatic full replacement or progress reset occurs.
- Preserve the SQLite `bank_versions` archives when upgrading, so previously queued scores can still be graded by their original answer keys. Keep private database backups and the corresponding bank JSONs together. Never reuse a bank version for different content.

## Privacy, boundaries and recovery

Snapshots are owner-authenticated and are never used as authority for ranking scores. They exclude sign-in tokens, recovery credentials and endpoint settings. Results are graded from answer IDs/choices against archived server keys. Rankings remain practice-only because offline keys can be inspected. The revised Android client explicitly opts in; older API registration represented joining the cohort and keeps its prior ranking behavior.

Facilitator reports contain aliases and aggregate learning evidence, not account credentials or question/answer text. Sharing is off by default, takes effect on a successful snapshot upload and can be revoked by unchecking it and syncing again. Faculty access requires the server-only faculty key plus the existing dashboard admin gate. Account deletion cascades to scores, snapshots and pending upload receipts. A student-chosen alias can still identify its owner.

The server retains one current snapshot per account and up to 200 upload receipts for retry deduplication. The client retains a durable in-flight upload in IndexedDB until a matching acknowledgement arrives. Snapshot size is capped at 1 MB and attempts are rate-limited. Keep a progress export as an independent backup. Server scoring does not verify student identity, motivation, proctoring or board readiness.

## Verification

`tests/sync-browser.cjs` exercises the real local API/SQLite with simulated HTTPS routing: original feedback drill, ranking/sharing consent, lost acknowledgements, duplicate protection, cloud recovery of an unfinished check, revision conflict, explicit restore, offline failure and same-version bank tampering. `tests/online-browser.cjs` checks the combined host's Streamlit WebSocket UI and authenticated API. `tests/test_sync.py` covers authorization, isolation, schema/body limits, replay conflicts, restart persistence, consent revocation and private enrollment. These are local software checks, not production hosting or physical Android validation.

Source: [Streamlit ASGI application API](https://docs.streamlit.io/develop/api-reference/server/st.app). The feature is pinned and exercised with the installed locked version rather than assumed from a generic server heartbeat.
