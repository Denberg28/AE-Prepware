# Faculty admin and corrections

Use a privately shared instructor dashboard. Student study accounts do not grant
admin permission. Editing and IN upload controls require a separate server-side
admin sign-in. No default password or embedded Android admin secret exists.

1. Run `.venv/bin/python scripts/admin_password.py` in a private terminal.
2. Add `AE_ADMIN_USERNAME = "your-admin-name"` and the returned
   `AE_ADMIN_PASSWORD_HASH = "scrypt$..."` to Streamlit Secrets (top-level TOML).
   Keep the plaintext password in your password manager. Never commit Secrets.
3. Open Question review and sign in. Passwords are verified server-side with
   salted scrypt and constant-time comparison. Sessions expire after one hour;
   signing out or changing credentials invalidates access. Five failed attempts
   in a browser session trigger a 15-minute wait. This is session-level throttling;
   use private Streamlit sharing/authenticated hosting for internet exposure.
4. Select an active question. Edit text, choices, key and explanation, enter the
   reviewer and a new bank version, and attest independent review. Saving retires
   the previous ID and appends a new reviewed ID with `supersedes`. Its original
   AI/IN origin remains visible. Retired questions stay available to old sessions.
5. Export the bank workspace/Android refresh. Dashboard edits are session memory
   until exported; restarts do not preserve unexported work. Load the saved bank
   workspace before continuing a later editing session.
6. Import a compatible refresh in Android Settings. All previous IDs, wording,
   choices, keys, explanations, citations and review metadata must remain intact.
   Progress, queued results, bookmarks and any ongoing session stay intact.
   A new active revision applies to future sessions. An unrelated full bank
   replacement is a separate explicit action that resets profile progress and
   is blocked with pending results; export before using it.

Export after editing, preserve the old bank/progress pair, and back up the API
SQLite database. The API archives bank versions and refuses to start with changes
to archived IDs or with different content under an existing bank version. Queued
old-bank results use archived keys; unknown versions fail with a recoverable 409.
Never delete archives while clients have queued results. An older APK may not
understand a new bank; downgrade requires its matching bank/progress backup.

See [instructor import contract](../instructor_uploads/README.md). Faculty review
of the original AI foundation bank remains pending. Admin approval of one edited
item does not imply approval of the other items or complete exam coverage.
