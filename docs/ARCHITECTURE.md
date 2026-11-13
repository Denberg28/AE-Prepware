# Architecture and contracts

Android Java Activity serves only packaged assets at `https://appassets.androidplatform.net/`. Remote navigation opens the system browser; the local file bridge is never given to remote HTML. Content Security Policy disallows inline scripts, frames and plugins. File/content access and mixed HTTP content are disabled. Native Storage Access Framework exports/imports JSON without broad storage permission; 2 MB limit. Back navigation returns Today and leaves a saved session.

`core.js` owns bank/state validation, subject aggregates, selection, shuffled order, answer locking, spacing, XP and session completion. `app.js` renders with escaped values and persists JSON to origin-scoped localStorage. Bank and progress schemas are versioned. This initial version has no previous migration. Current session writes happen after each answer and step. Export before uninstalling; encrypted device storage protection depends on Android configuration. No analytics, ads or background job.

Daily local quests use the device calendar and are motivational only. Cohort points use server dates in Asia/Manila and do not trust client clocks or XP. Ranking compares daily unique-correct points, then total correct. Incorrect answers count in attempts; no negative points. Offline keys are distributed with the app, so this is not an anti-cheat system. Names are self-asserted and account tokens are unrecoverable after signout unless the device retains them. No email/password collected.

## Optional API

FastAPI + SQLite; run one API worker, persistent disk, HTTPS reverse proxy. `AE_BANK` optionally selects an entirely instructor-approved JSON bank; otherwise bundles source-checked foundations. App/API exact bank version agreement required. A server bank replacement invalidates unfinished older challenges. Public exposure requires TLS, request/connection rate limiting at the proxy, disk capacity monitoring and restricted server administration. The service caps application POST bodies at 16 KB and applies SQLite-backed registration/challenge/submit limits. IP registration limit is per direct peer: configure a trusted proxy and do not trust arbitrary forwarded headers.

| Method/path | Input | Result |
| --- | --- | --- |
| GET /health | none | schema, service and bank versions |
| POST /participants | name (2–30 letters/digits/space/period/hyphen/underscore) | random ID/token; token stored hashed |
| GET /leaderboard | none | top 100 submitted participants, points, correct, attempts |
| POST /challenges | bearer token | 20 weighted question records without key/explanation; reuse unsubmitted challenge |
| POST /challenges/{id}/submit | bearer; 20 distinct {id, choice:0–3} | score, daily credited points and review; idempotent |
| POST /participants/delete | bearer | cascaded deletion of participant, challenges, credits and submissions |

Challenge expiry: 24 hours. Server `BEGIN IMMEDIATE` transactions make grading/crediting/retries atomic. SQLite foreign keys enforce ownership cleanup. No client-supplied XP, elapsed time or total is accepted. Persist database backups with access controls; they contain pseudonyms, hashed tokens and educational scores. Invalid JSON produces bounded validation errors; API traces are not returned to clients.

## Faculty Streamlit dashboard

Run on localhost or behind an authentication gateway; it is not an administrative API for students. A template study plan works without credentials. Optional Gemini coursework generation uses `GEMINI_API_KEY` on the server, configurable `GEMINI_MODEL`, timeout and output limits. Failure leaves the local template available. The AI service receives only selected subject/topic, never participant history. Live AI output has not been validated without a configured key.

Review work is session-scoped until exported. Per-question instructor approval requires name and independent-verification checkbox. All questions must be approved and bank version changed for an Android-importable export. Review is an educational workflow, not a digital-signature/authenticity guarantee: only import banks from a trusted instructor.
