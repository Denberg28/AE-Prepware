> Historical v0.1 baseline specification. Current v0.2 flow and acceptance criteria: [V0_2_SCOPE.md](V0_2_SCOPE.md).

# AE Prepware 0.1 MVP specification

## Baseline and assumptions

2026-11-13: confirmed public repository `Denberg28/AE-Prepware`, default branch `main`, initially empty (no commit, release, package ID or signer). Shared `Denberg28/Agents_md` rules copied intact, followed by project-specific additions. There is no known-good earlier artifact to roll back to.

Android 8.0/API 26 or later, updated Android System WebView, portrait/landscape, no paid dependency. Package identity `ph.diversify.aeprepware`. Native Java host with local HTML/CSS/JavaScript UI minimizes APK size and avoids a cross-platform framework. Local WebView storage is primary, JSON backup portable. Streamlit is the faculty dashboard, not a phone database; SQLite on the optional API server holds shared cohort records.

## User flow

Today → recommended adaptive session → one multiple-choice answer → explanation/reference → next → results/review → progress. A saved session survives closing/reopening. Study offers subject practice, shuffle, bookmarks, mistakes and a 20-item weighted check. Settings exports/imports progress and locally sets aside disputed items. Cohort → enter instructor HTTPS URL and pseudonym → join → server-issued challenge → submit → ranking. Faculty dashboard → focus topic → coursework plan → optional AI draft → human question review → approved bank export → Android import.

## Scope

72 original foundation questions, 12 per subject; each has four options, one key, explanation, topic, reference and author review metadata. Subject weights verified against PRC November 2026 examination program: mathematics 10%, aerodynamics 25%, structures/design 20%, construction/repair/modification 15%, powerplant 20%, economics/management/laws/ethics 10%. Independent faculty review is pending; this is not comprehensive syllabus/TOS coverage.

Adaptive rules prioritize weaker subjects using smoothed accuracy, missed items, unseen items and due review. Intervals after correct streaks: 1, 3, 7, 14, 30 days; incorrect answers become due in 10 minutes. Randomization and recommendation are local rules, not an LLM. Optional server-side AI drafts coursework plans only; it never grades or changes keys.

Non-goals for v0.1: full-length/proctored board exam, a pass probability or 100% guarantee, paid subscriptions, automatic AI question publication, verified student identity, high-stakes anti-cheat, social messaging, app-store publication, hosted API provisioning. The shared-ranking service is included and runnable, but requires instructor HTTPS hosting.

## Interfaces and recovery

- Bank JSON schema 1, stable question IDs, correct option indexes 0–3, six fixed subject weights. Imported banks require every question approved with named reviewer/date. Changing banks resets local progress after confirmation.
- Progress schema 1 and exact bank version; invalid imports are rejected before mutation. Unknown/corrupt local records are preserved for raw export; recovery requires explicit confirmation. Cohort token is excluded from backups.
- API v1 contract in ARCHITECTURE.md. HTTPS-only Android requests, 12-second timeout, no automatic retry, retry-safe challenge submit. No internet leaves offline study available.
- Quiz answer locks immediately, each recorded once, option order persists. Save failure blocks further study and offers export/recovery. Uninstall/clear storage requires restoring an exported backup.
- Cohort service stores random hashed bearer credentials; account deletion cascades records. Names are public to the cohort. Local history never uploads automatically.

## Measurable acceptance criteria

1. All 72 bundled records pass schema/reference/key checks; no unreviewed AI drafts in scored bank.
2. A 20-item weighted check has 2/5/4/3/4/2 items in the documented subject order and no duplicate ID.
3. One tap records one answer; additional taps do not increase attempts or XP. Repeating an item does not farm daily XP.
4. Reload preserves question, selected answer and shuffled order. Complete session shows exact correct/total and review explanations.
5. Weakest-subject fixture receives priority; reported items excluded from future sessions; empty pools explain recovery.
6. Corrupt/unsupported backup is rejected and existing data remains; a valid backup round-trip preserves history/session.
7. API grades issued IDs on server, rejects malformed/duplicate IDs and cross-participant submission, and repeated submit has identical score with no double credit. One question earns at most one point per participant/server day (Asia/Manila).
8. No HTML execution from display names, imported content or server names. No signing key or API key in tracked source.
9. APK under 5 MB, successful assemble/lint, valid APK signature and manifest API/package inspection. 320–780 px layouts have no horizontal overflow; local question navigation under 250 ms in desktop test (device timing pending).
10. Candidate gates: automated tests, source review, build/lint and packaging pass; absent phone/AI/host validation disclosed. Stable requires physical Android installation/resume/SAF backup/device tests and independent faculty bank audit.
