# Instructor uploads (IN)

Put only instructor-owned or redistribution-authorized question JSON here. This
repository is public: do not commit copyrighted commercial test banks, private
student data, passwords, keys, or unlicensed PDFs. Keep restricted teaching
sources privately; the editor accepts local reviewed JSON without publishing it.

IN means instructor-uploaded. AI means AI-produced, even after instructor review.
Changing a correct answer never changes the old ID: use the admin revision editor.

Upload format: schema 1, a unique `version`, the six `subjects` entries copied from
`app/src/main/assets/bank.json`, `sources`, and a nonempty `questions` array.
An upload may contain only one subject. Each source needs a title, HTTPS URL and
precise locator. Each question needs the normal bank fields plus:

```json
{
  "id": "IN-AERO-0001",
  "origin": "IN",
  "upload": {
    "file": "instructor-aerodynamics-2026.json",
    "locator": "Question 1 / page 1",
    "rights": "instructor-original"
  },
  "review": "approved",
  "reviewer": "Actual instructor who independently checked this question",
  "reviewedAt": "2026-11-13"
}
```

Allowed rights: `instructor-original`, `permission-granted`, `public-domain`,
`open-license`. A rights label is the uploader's attestation; it is not a legal
verification. Include licensing details in the source locator where applicable.
Do not mark extracted questions approved until a qualified instructor checks the
prompt, three or three or four distinct choices, unique correct answer, explanation, source/page
and subject mapping. Figure-dependent or ambiguous items need manual resolution.
Do not substitute AI explanations without review. Existing IDs or conflicting
source IDs are rejected, atomically. Up to 3,000 total archived + active records;
Android JSON imports are limited to 8 MB.

Admin: Question review → sign in → Add instructor questions → export refresh.
Alternatively:

```sh
.venv/bin/python scripts/merge_instructor_bank.py instructor_uploads/reviewed.json \
  --version 2026.11-instructor.1 --output /private/AE-bank-refresh.json
# Use --base /private/current-bank.json after the first update.
```

Install the exact export in Android Settings and start the API with
`AE_BANK=/private/AE-bank-refresh.json`. Export phone progress and back up the API
SQLite database before updating. Preserve its `bank_versions` table so old
queued sessions can be graded using their original keys. A brand-new API cannot
grade a bank version it has never archived. Restart each single-worker API only
after exporting the current bank; no live file watcher changes scored keys.

AI-only and IN-only require 50 active, unreported questions in the subject.
Hybrid requires 25 AI + 25 IN. Empty or insufficient pools are unavailable;
questions are never duplicated to fill a session.

The earlier session's reported 2,005-question IN import was not present in the
recoverable repository. No reconstructed commercial question corpus is included
or claimed here. All six IN pools start empty until reviewed content is imported.
