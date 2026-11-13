# AE Prepware v0.4.1-rc.1 · Signed test candidate

Keeps the AE Prepware/Settings header and bottom navigation stationary on every
screen, including the questionnaire. Only the center pane scrolls. Next question
and tab changes reset the center without moving either bar.

Removes the large subject heading, guest signup prompt, repeated instructions and
per-card exam-weight text. Keeps compact bank/session status and source counts.
Uses consistent readable type, answer spacing and touch targets. Review status
and detailed bank notices remain in Explanation/Settings. Consolidates duplicated
CSS into one stylesheet and adds scrolling/visibility/session regression checks.

Supports original three-choice IN content, mixed three/four-choice sessions,
large private banks in IndexedDB, bank export, and an 8 MB JSON transfer limit.
Existing account/progress formats and permanent signing identity are retained.

The PUBLIC APK contains 360 original AI foundation questions. The user-supplied
books are available only in the separately delivered PRIVATE study build:
2,003 source-key-matched IN questions, with 67 figure/ambiguous items held.
Original A-C choices and explanations are retained. Source-key agreement does
not mean independent faculty review or current Philippine regulatory validation.
No Mathematics or Philippine Laws/Ethics IN pool comes from these books.

Install over the permanently signed v0.2/v0.3/v0.4 app without uninstalling; export
both progress and the current bank first. Package ph.diversify.aeprepware,
versionCode 5, same certificate. Physical Android insets, keyboard, installation,
upgrade and accessibility validation remain pending. Candidate only; no stable
or board-pass claim. No new production service or live AI deployment.

Retain old APK and matching bank/progress backups for rollback. Android blocks
lower-version installs; uninstalling erases local data. Old APKs do not support
new three-choice private banks or IndexedDB bank storage. Do not downgrade
without exporting the correct backup pair first.
