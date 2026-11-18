# UI refinement — 0.8.3-rc.1

## Scope and baseline

Repository: Denberg28/AE-Prepware; source baseline: `74c0bf812f99298663e82aca836c5f8d11544fbe` on main (0.8.2-rc.1).
The previously packaged candidate is retained; physical Android evidence remains absent.
This is a focused Android WebView UI update. No new runtime dependencies, bank changes or data migrations.

Keep the simple Subjects screen, sun/moon control, explicit Sync and fixed header/navigation. No principle banner or bearing/heading/throat shortcut.
Use local SVG symbols plus explicit text; retain source counts and PRC weights. Study set → source choice → subject → answer → explanation/next → result remains the primary flow.
Continue resumes the saved session. Empty source pools explain the next action.

## Changes and acceptance

| Area | Expected behavior | Check |
| --- | --- | --- |
| Subject/navigation hierarchy | Six readable subject cards; weights/source counts; icon and text navigation | Existing shell/theme tests and ui-browser |
| Layout | Only center scrolls; chrome stays reachable at 320×480, 393×760 and 720×480, including enlarged text | shell-browser, theme-browser, ui-browser |
| Readability | Consistent surfaces and larger choice targets; normal text contrast at least 4.5:1 in both themes | theme-browser |
| Answer state | One selected answer stays visible after reload; deferred checks reveal no correctness/explanation before submission | readiness-browser, ui-browser |
| Keyboard access | Navigation/next focuses heading; answering focuses feedback and next Tab reaches explanation | ui-browser |
| Recovery | Unavailable source pool explains changing bank/study set; confirmation has accessible title/body | ui-browser |
| Regression | Question IDs/keys, sessions, source quotas, offline accounts and sync preserved | Existing Node/Python/browser suite |
| Android | Debug/release build and lint pass | Existing verify workflow |

## Verification and delivery

Run `node tests/ui-browser.cjs` alongside the existing workflow. It saves synthetic-data screenshots in CI artifacts for light/dark and small/large layouts.
The existing workflow runs Node/Python tests, dependency audits, browser regressions and Android assemble/lint.
Local execution was unavailable during this edit; report actual workflow results separately and do not label checks passed before observing them.

This branch increments the planned candidate version to 0.8.3-rc.1 / code 12 so the old signed package cannot be mistaken for this update.
No permanent signing key is available in this execution environment. Signed APK preparation, on-phone update, TalkBack, native font scaling, system bars and lifecycle remain BLOCKED / NOT TESTED.
Existing publication guards must remain intact; an unsigned development artifact is not an installable published candidate.

Rollback: retain 0.8.2-rc.1 and revert this focused source commit before packaging if necessary.
No state migration was introduced. Never uninstall an installed app without exporting progress and the matching private bank.

## 18 November 2026 — Review-focused simplification

Baseline: `92e9605` on main. Source version remains the unpublished 0.8.3-rc.1; no signed package is produced by this source change.

Subjects now lead with Continue when a session exists. Practice options groups scope, sources and selection behind one native disclosure, collapsed on launch. The chosen question count/source remains visible. Compact subject cards retain names, PRC weights and bank counts. Missing pools direct the user to Practice options, including when both sources are deselected.

Results starts with saved session count, practice accuracy and history. Study checks & monitoring is optional and collapsed on launch. Submitted sessions show expanded mistakes first and place correct answers in a separate disclosure. Explanations remain optional. Diagnostic answers are still withheld until submission; no content, scoring, account, sync or storage format changes.

Acceptance: options stay open when changed; choices persist through re-render/reload; resume and source quotas remain exact. A 14/20 diagnostic shows six expanded mistakes and fourteen optional correct answers; a 20/20 result shows the all-correct state. Existing browser journeys exercise explicit disclosure opening plus themes, focus, small widths and enlarged text. See the current checkpoint for observed verification results. Physical phone validation remains pending.
