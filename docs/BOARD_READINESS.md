# Board Readiness Monitoring System — v0.8

Open **Results** in the Android app. The student dashboard separates recorded participation, competence evidence and readiness signals. Faculty can review voluntary JSON reports in the existing private Streamlit dashboard's **Board readiness** tab after admin sign-in. No new service, paid API or background telemetry is required.

## What is measured

| Dimension | Evidence | Interpretation |
| --- | --- | --- |
| Commitment | Distinct questions answered per Philippine-calendar day, active days over 7/28 days, progress against a configurable study-day goal | Recorded app participation. It does not establish motivation, effort, review attendance or study outside this app. |
| Competence | First answer to each previously unanswered item; first completed diagnostic; latest eligible check per subject; first-attempt topic gaps | Performance on the available bank. Original first responses are not overwritten by later correct repetitions. Legacy first outcomes remain unknown. |
| Readiness signals | Recent checks in all six subjects, seven-day confirmation, PRC-weighted practice results, missing evidence and subject-support priorities | Descriptive foundation targets. No pass probability or certification of full board readiness is produced. |

The seven-day activity goal defaults to **4 days with at least 10 distinct answers/day**, configurable to 1–7 days and 1–50 answers. Reopening the app, leaving it idle, or tapping an already answered choice does not add activity. Participation from an unfinished check is recorded; its competence result is withheld until submission. All days use Asia/Manila, independent of the device's display timezone. A new journal shows an unobserved window, not a low-commitment classification.

## Diagnostic and retention workflow

1. Choose AI, IN or both in Subjects. In Results, use a subject's **New-item check**. It selects 20 active, non-set-aside items from the full bank, or 10 from each selected source in Hybrid. Items previously answered in this profile, including known prior revisions, are excluded. Unseen items may still resemble previously studied calculation families; novelty is not an assurance of unfamiliar concepts.
2. Answers lock immediately. Feedback, explanations and competence updates appear only after all 20 answers are submitted. Save/exit and app restart preserve answers and their times. These are self-paced, unproctored checks; offline keys remain inspectable.
3. **Spaced recheck** requires 20 eligible previously answered items (10 per source in Hybrid), each unanswered for at least seven days. It uses the same deferred-feedback flow.
4. A subject foundation target requires the latest eligible check at **80% or above**, plus another successful check at least **7 days earlier**, both within the last **30 days**. The 80% target is a product study rule, not the legal PRC passing rule. A check spanning over 24 hours, or containing a retired/set-aside item, cannot qualify. Historical scores remain unchanged.

Subject states distinguish **Baseline needed**, **Recheck due**, **Support needed**, **Confirm retention** and **Foundation target met**. Missing evidence is not treated as an incorrect answer. Weak subjects are prioritized using observed performance and official subject weight; unassessed subjects are explicitly identified as needing assessment. First-attempt topic gaps require at least three observed items before a topic is listed.

The PRC-weighted foundation percentage is displayed only when every subject has a recent eligible check. Missing subjects are never omitted and remaining weights are never renormalized. Random forms are not equated or validated as predictors. The first recorded diagnostic is retained separately from the rolling history; it is not necessarily a pre-review academic baseline. No improvement or failure is attributed to facilitators, lecturers or student motivation by this software.

The current 240-item private core and 120-item public core have incomplete PRC coverage and pending independent faculty validation. Consequently, **board readiness remains “Not established,” even if all six foundation targets are met**. See the 2022–2026 bank review for content gaps.

## Voluntary facilitator reports

Expand **Facilitator report**, choose an alias, and export the JSON. A confirmation explains the disclosure. Reports contain aggregate activity, first-attempt counts, check summaries, baseline results, topic labels and the bank version. They exclude account numbers, recovery credentials, sign-in tokens, question stems, choices and answer keys. A stable random profile identifier allows the latest report from the same profile to replace an older report. An alias can identify its owner; the student decides whom to share it with. No report is automatically uploaded to the cohort API or public ranking.

Faculty workflow:

1. Run `streamlit run streamlit_app.py` locally or behind an authenticated private host, using the existing faculty admin configuration.
2. Sign in under Question review, then open Board readiness.
3. Open up to 50 voluntarily supplied reports, each no larger than 200 KB. Invalid files are excluded individually. The newest report per profile is displayed; a short profile suffix disambiguates repeated aliases.
4. Review missing assessments, subject-support needs and report age. Check freshness is recalculated at import; activity describes the reported seven-day window. Different bank versions and random forms should not be ranked as equivalent measures of ability.
5. Download a CSV for facilitator follow-up. CSV cells are hardened against spreadsheet formulas. Uploads remain in the dashboard session and are not stored in a new database.

Use the information to discuss access, transportation, attendance, prerequisite knowledge and study support. A weak score or low recorded activity alone cannot explain an examination failure, establish lack of commitment, or support causal blame or student exclusion.

## Persistence and compatibility

Full online synchronization is now supported through the upper-right Sync control. It preserves the local journal in an owner-only snapshot. Faculty sharing remains a separate opt-in. For deployment, revision conflicts, private bank enrollment and recovery steps, see [online synchronization](ONLINE_SYNC.md). The server grades scores separately from these device-recorded summaries; neither source establishes proctored board readiness.

The journal is per profile and works offline. It retains 28 days of distinct daily item IDs, at most 3,000 first observations, six initial diagnostic summaries, and check evidence from the latest 200 saved sessions. Daily IDs are pruned; the original diagnostic is retained after history rotation. No idle timer or service polling is added.

Progress exports include the journal, goals, baseline and unfinished checks. Guest-to-account binding and local sign-in preserve it. Existing score synchronization accepts completed 20-item checks using the unchanged answer payload. **Full Sync backs up this journal, diagnostic classifications, goals and unfinished checks to the owner-only snapshot. Cloud recovery merges that snapshot with any newer server-graded results. Export a progress backup as well before reinstalling or changing phones.** The private bank must accompany a backup that references private IDs. Older app versions do not understand the new monitoring semantics; keep the previous APK and matching backups rather than assuming a downgrade conversion.

All data is device-recorded and can be edited by its owner. A clock change can invalidate check timing. Faculty reports are summaries, not verified audit trails or proctored examination records. No official readiness claim is possible without validated content, assessment procedures, external outcome evidence and appropriate review.

## Rationale and validation boundary

The [IES practice guide](https://ies.ed.gov/ncee/WWC/PracticeGuide/1/Published) supports retrieval practice, delayed review and identifying material that needs further learning. It does not validate this app's numeric cutoffs. The [Standards for Educational and Psychological Testing](https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards_2014edition.pdf), especially Standard 1.0, require evidence for intended score interpretations. These references inform the design; they do not make these bank scores a validated PRC predictor. Policy `brms-1` records the current descriptive rules so future changes require explicit versioning and verification.
