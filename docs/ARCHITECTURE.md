# Architecture and contracts — v0.2

Android Activity serves packaged HTML/CSS/JS at `https://appassets.androidplatform.net`. Native JSON file bridge is exposed only to local content; remote navigation opens the system browser. CSP excludes inline scripts/frames/plugins, file/content access is disabled, HTTPS is required for APIs and external links. Exports/imports use Android Storage Access Framework with a 2 MB input/output limit. Back saves the current session and returns Subjects. WebView must be current for Web Crypto/structuredClone.

## Study and account state

`core.js`: validates bank/state, shuffles questions/choices, locks answers, maintains attempt stats and spacing, caps daily local XP, records complete sessions and queues account-bound 50-item results. `accounts.js`: random 16-digit AE account number, 256-bit random recovery code, SHA-256 local verifier, bounded local account directory and profile storage. Number is an identifier; the high-entropy recovery code is the authenticator. Local profile storage is a convenience boundary, not encryption against an unlocked-device user.

`app.js`: minimal Subjects/Results/Ranking/Account UI. Random default, adaptive missed/unseen preference, optional connected AI topic selection. A question choice is stored as its canonical index; the displayed letter is derived from the saved permutation, so explanations cannot mislabel shuffled answers. `details` explanation panes start closed. Session answer/order/index is persisted after every change. Score and question/answer details are recorded after all items are answered. Queue is persisted before any network operation; server acknowledgement removes it only after identity/grade validation. At 200 pending records, new sessions stop and sync/export is requested. Latest 200 history entries retained; server keeps all synchronized attempts in aggregate.

Guest storage `ae-prepware-v1` and the original question IDs remain valid. Account profiles use `ae-profile-<number>` and imported banks use `ae-bank-<number>`. Account index contains number/name/verifier, never a recovery code. New account creation links guest history on that device, but earlier guest sessions cannot be submitted for ranking because their account-bound evidence is absent. Imported progress must match the signed-in account and bank; legacy foundations.1 guest backups can load against foundations.2 because their original IDs/keys remain unchanged. Switching approved banks resets only the current profile after confirmation and is blocked while results need sync. Backups omit API tokens; recovery files are separate. No automatic email/password reset, identity verification, telemetry or ads.

## Optional HTTPS API

FastAPI/SQLite, one worker and persistent disk. Original v0.1 participant/challenge tables and endpoints remain available; account tables are additive. No destructive migration. Account registration/login returns bearer tokens; DB stores SHA-256 token hashes and salted scrypt recovery verifiers (N=16384, r=8, p=1). A token lasts 30 days; up to five devices. Logout revokes the current token; deletion cascades through account results, tokens, progress and credits. Database backups contain sensitive educational data and verifier hashes and must be private.

| Method/path | Contract |
| --- | --- |
| GET /health | schema, bankVersion, app version |
| POST /accounts/register | number, name, recovery; idempotent for matching credentials; returns token/profile |
| POST /accounts/login | number and recovery; returns token, last 200 results, complete synced aggregates |
| GET /accounts/me | authenticated account profile/history/progress |
| POST /accounts/results | session ID, subject, bankVersion, exactly 50 distinct canonical {id,choice} answers |
| POST /accounts/plan | authenticated subject and optional ai=true; 50 source-bank IDs and selection status |
| GET /accounts/leaderboard | display name, masked suffix, points, correct, attempts; no full number/token |
| POST /accounts/logout | revoke current authenticated token |
| POST /accounts/delete | permanently delete authenticated account and dependent rows |

POST limit 16 KB; SQLite-backed registration/login/selection/submission limits. All mutable result scoring/credit updates use BEGIN IMMEDIATE. Same account/session ID + identical payload returns the original grade; changed answers under that ID get 409. Questions must exist, be unique, same subject and exact bank version. Server recomputes correct count; never accepts client score or XP. Credits use server day Asia/Manila and at most one credit per account/question/day. Offline answer keys are distributed, so rankings are practice motivation, not an anti-cheat or proctored assessment service. No client clocks determine awards.

CORS allows the packaged origin and optional explicitly configured AE_DEV_ORIGIN. Operator must supply TLS, proxy request/connection rate limits, persistent disk/backups and admin controls. IP buckets use direct peer; don't blindly trust forwarded headers. A service failure leaves offline study, account state and pending results intact. Service URLs are user supplied HTTPS roots with no embedded credentials/query/path. Provider/service redirects are not followed.

## AI boundary and Streamlit

Optional account plan uses only server aggregate topic counts. With server GEMINI_API_KEY/model configured, Gemini can choose up to three exact topic names. Response parsing rejects unknown or malformed topics; missing key/quota/network failures fall back to local server adaptive rules. Selection returns only validated existing IDs. No provider output is scored, and no name, account number, token or recovery code is sent to Gemini.

Streamlit remains a separately hosted private faculty dashboard. Secrets support and root entry are preserved. Optional generated coursework is a labeled instructor-review draft. All question approval/export remains explicit and session-scoped; export work before reboot. Use account ranking endpoint for current standings; legacy cohort ranking remains separate. Streamlit Secrets do not provision a separate FastAPI server's environment.

## Signing and publication

release.json pins versionCode, version and permanent certificate fingerprint. Private signer is backed up separately; public certificate is committed. Source commit is built and signed privately; a subsequent commit adds the prepared signed APK plus source digest, checksum and public reports. CI independently rebuilds and compares all ZIP payload entries except the changing VCS marker, verifies cert/manifest/assets/digest, and publishes the same signed bytes only after required gates. No private key is committed, uploaded to CI, or included in APK.

Initial transition from v0.1 requires backup/uninstall/reinstall because its CI debug private key is unavailable. v0.2+ updates must raise versionCode and retain the permanent signer. Physical Android install/update/content review still gate stable release.


## v0.3 provenance and bank lifecycle

`origin` is AI or IN (legacy records default to AI). IN additionally requires
approved review metadata and upload file/locator/rights. Session selection uses
only active, unreported questions: one source 50 or Hybrid 25 each. AI topic
planning obeys the same quotas and cannot generate scored keys.

Faculty editing is behind separate server-side scrypt authentication. Every
correction retains the original origin and appends an approved ID with
`supersedes`; the old ID becomes inactive for future draws but remains available
for old sessions/results. `extends` links an exported refresh to its starting
bank version. Existing grading/display/citation/review fields are immutable.
Multiple dashboard edits in one workspace export one refresh from its baseline.
Mobile validates compatibility before persisting the new bank, leaving progress
untouched. Persistence failure leaves the old in-memory bank and state intact.
A crash after the new append-only bank is stored still has a compatible old state.

The service snapshots full banks in SQLite bank_versions and refuses reused
versions with different content or mutation/removal of archived IDs. Queued
results use their archived version, not the current key. Server bank activation
is an explicit single-worker restart with the exported file; there is no live
mutable scoring endpoint. Restricted source documents stay outside public git.

## v0.6 bank focus and compatibility

Optional `focus` metadata selects immutable question IDs and maps each to a PRC area. Each area records the printed 2010 TOS item count; this does not claim complete competency coverage. Validators reject unknown/retired IDs and subject mismatches. Default core sessions contain 20 items (Hybrid 10 each); full-bank sessions remain 50 (Hybrid 25 each). Topic diversity follows local/server priority ranking. API plans default to full for older clients and accept an explicit `scope`. Results accept exactly 20 or 50 distinct, same-subject answers; historical archives and retry identity remain authoritative.

`profileBank` upgrades a stored snapshot only when the bundled version directly extends it, every old question/citation is unchanged, and saved progress validates against the new snapshot. Persistence precedes replacement in memory. Other stored banks survive. Private classification corrections retire old IDs and append source-key-verified copies; no historical subject or answer is rewritten. Admin revisions transfer core membership to the approved revision.

## v0.7 monitoring

`readiness.js` provides descriptive, versioned `brms-1` calculations. A per-profile journal stores 28 activity days, up to 3,000 immutable first outcomes and six initial diagnostic summaries. Existing history provides bounded check evidence. `core.js` records activity at an answer but grades new diagnostic/retention modes only at successful completion; original practice/legacy behavior remains compatible. New-item selection follows prior `supersedes` chains and source quotas. Checks preserve times/eligibility through restart. The report projection excludes credentials and question text/keys.

The faculty importer recomputes target states and weighted scores from bounded check summaries rather than trusting uploaded readiness labels. It does not authenticate device observations. Admin-gated manual uploads and a hardened CSV create no new service or database. Existing answer-only result sync is unchanged; remote account recovery restores scores without the local monitoring journal. Cloud history is not reclassified as diagnostic evidence.


## Full profile synchronization

See `ONLINE_SYNC.md`. Owner-only snapshots use optimistic revisions plus operation IDs and a durable client upload copy. Server-graded result history remains separate from snapshots and voluntary facilitator reports. Snapshot restore preserves first-attempt observations and merges newer server results. Ranking consent is stored independently, and private bank downloads require per-account enrollment. The combined ASGI runner mounts Streamlit at `/dashboard` beside the API. Production persistence/TLS is a deployment requirement, not an assumed feature of Streamlit Community Cloud.
