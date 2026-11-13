# v0.4.0-rc.1 verification · 2026-11-13

Baseline e88c57d / public signed v0.3.0-rc.1. User supplied phone screenshots and
2019 Airframe / 2018 Powerplant guides. Scope: system-bar spacing, compact padding,
label visibility and usable private IN banks. Uploaded PDFs remain unchanged.

Self-reviewed evidence; physical phone behavior is not inferred from a browser:

| Gate | Status | Evidence |
| --- | --- | --- |
| A/B/C Node | PASS | 24 tests: old account/scoring/backup behavior, source quotas, private provenance, 3-choice restore/grade/queue and mixed 3/4 choice permutations |
| A/B/D Python | PASS | 28 pytest tests: API/auth/editor/archives, private review scope, 3-choice server grading, mirrored-column synthetic PDFs, footer-key/explanation boundaries |
| B/C browser | PASS | Existing study/source workflows plus private bank sessions, IndexedDB/account copy, a later public-app upgrade, source labels, contrast >=4.5, 320/393 px and enlarged text |
| D real local API | PASS | Actual FastAPI/SQLite grades and recovery/retry/ranking workflow; HTTPS origin simulated |
| Private input extraction | PASS for stated structural/key scope | 2,070 source questions detected; 2,003 included / 67 held; all 2,003 keys independently agree with Poppler footer text; private bank validated in Python and in the actual browser app |
| A dependencies | PASS | Pinned PyMuPDF 1.26.7 authoring dependency audited; backend/npm audits apply. No unresolved reported vulnerabilities |
| A Android | PASS | Debug/release assemble and lint with SDK/build-tools 35 and Gradle 8.10.2; API 26 supported; API 27 theme override keeps navigation contrast API-safe |
| F public packaging | See public manifest / CI | Existing pinned certificate, versionCode 4, source digest and full rebuilt payload; verifier rejects private guide banks |
| F private packaging | See private manifest / APK-VERIFICATION | Same certificate/package, bank checksum, audit count, every asset and full unsigned payload checked; never placed in public release paths |
| E/F physical device | NOT TESTED | Android 16 insets/keyboard, real installation/upgrade, SAF and accessibility still require phone confirmation |
| Independent content approval | BLOCKED | Source-key match is not independent faculty review, current Philippine rule verification or complete PRC TOS mapping |

Public tests use original synthetic records only. No original guide text, private
banks, PDFs, signing credentials or recovery codes enter public git/CI artifacts.
Private extraction results and review queue are delivered to the user separately.
Source-key-verified private IN metadata is explicitly distinct from approved
faculty material. Original A-C choices are retained; no D is invented.

The native parent consumes system-bar/cutout/IME insets, leaving the WebView a
bounded content viewport. Browser screenshots verify web layout/contrast only.
Legacy localStorage banks remain readable; new banks use IndexedDB. Bank export
and progress export are both needed before reinstall/downgrade. Existing signed
v0.2/v0.3 update identity is retained; old APKs cannot read new private bank formats.
