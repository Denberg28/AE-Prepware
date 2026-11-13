# v0.4.1-rc.1 verification · 2026-11-13

Baseline 434f1c7 / signed v0.4.0-rc.1; user requested steady header/navigation,
center-only scrolling, removal of headings/instructions, standard readable text
and stylesheet cleanup. The private IN corpus/keys and account schemas are unchanged.

| Gate | Status | Evidence |
| --- | --- | --- |
| A/B/C core/API | PASS | 24 Node + 28 Python tests; grading, shuffled keys, account isolation, queues, private bank provenance and existing storage behavior |
| B/C shell/browser | PASS | Header/nav geometry stays fixed during center wheel/long-question scrolling; document scroll stays zero; no content overlap; next/tab reset; saved session restored; 320/393/720 widths and enlarged text |
| B/C baseline browser | PASS | Existing study, source/refresh, private-bank persistence and actual local API recovery/retry workflows |
| Private corpus | PASS for unchanged-data scope | Same 2,003 IN + 360 AI records, bank version and source keys retained; actual private bank exercised by browser workflow |
| A Android | PASS | Debug/release assemble and lint, SDK 35/build-tools 35.0.0, Gradle 8.10.2/JDK 21 |
| F public/private packages | See manifests / verification reports | Same permanent certificate/package, higher versionCode 5, source/asset/unsigned-payload/checksum verification. Private content excluded from public git/release |
| Physical phone | NOT TESTED on this revision | Fixed chrome, Android system bars/keyboard, real installation/update and accessibility require phone confirmation |
| Faculty review | BLOCKED | Existing source-key checks do not imply independent faculty approval |

The header and nav are non-scrolling flex siblings of one bounded overflow pane.
No stacked fixed/sticky offsets cover content. Scroll resets target that pane;
feedback scrolls into it without moving app chrome. Review provenance and bank
limitations remain available in Explanation/Settings; they are removed from the
normal question/subject flow. The stylesheet replaces duplicated overrides.

Self-reviewed candidate evidence only. Export progress and the current bank before
updating/reinstalling. Keep v0.4 and matching backups for rollback; Android blocks
lower-version installs and uninstalling erases local data. Private bank content
and the 67-item review queue remain separate private deliverables.
