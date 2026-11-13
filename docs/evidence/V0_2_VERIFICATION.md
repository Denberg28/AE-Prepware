# v0.2.0-rc.1 verification — 2026-11-13

Baseline: source 50eb1b3 and published v0.1.0-rc.1. Self-review only. Scope: 50-question minimal Android flow, expanded foundations, account/result/selection/ranking service and permanent signing. Source commit/digest/artifact identity are recorded in the prepared release manifest.

Environment: Linux x86_64, Python 3.12 venv, Node 24, Playwright 1.58.2 with local Chrome headless shell 131, JDK 21.0.13, Gradle 8.10.2, SDK35/build-tools35.0.0. GitHub uses its pinned Playwright browser and supported Ubuntu24.04 runner. Installed Gradle distribution used offline locally because wrapper bootstrap network was unavailable.

| Gate | Status | Evidence/limits |
| --- | --- | --- |
| A/B/C: core/accounts | PASS | 18 Node tests: 360 questions, correct weights, 50 unique same-subject picks, score/locking/shuffle/resume/XP, profile isolation, recovery verifier and bounded result queues; old guest schema retained. |
| A/B/D: bank/API/dashboard | PASS | 21 pytest tests: original 72 stems/choices/keys unchanged, distinct stems, numerical fixtures, legacy API regression, salted recovery/token expiry, account isolation, server grading/deduplication/conflicts, masked ranking, logout/deletion, allowlisted provider selection/fallback and Streamlit root/Secrets regression. |
| B/C: UI | PASS | Playwright full 50-question session: 49/50 exact score, wrong displayed-letter mapping, explanation collapsed/open, reload resume, create/recover account, backup cancel/restore, malformed/corrupt storage handling and legacy 10-item resume; 393/320 widths. |
| D: actual local integration | PASS | Browser → real FastAPI → SQLite → account ranking. Dropped acknowledgement AFTER server commit; retry leaves 50 attempts, not 100. Separate browser context restores same account and synced progress. HTTPS origin simulated, no live TLS claim. |
| A: Android build/lint | PASS | assembleDebug/assembleRelease/lint; no lint errors. Final committed source is rebuilt before signing. |
| A: dependency review | PASS | pip-audit: no known vulnerabilities; npm audit: zero. No new third-party runtime dependency. |
| A: content/source self-review | PASS | Original parameterized exercises with explicit assumptions/sources; duplicate generated shaft-power stem caught and corrected. Faculty review still required. No private key/recovery/password/API key tracked. |
| F: permanent certificate backup | PASS | Private 3072-bit RSA signer generated and private recovery archive saved. Public certificate SHA-256 pinned in release.json; previous CI debug certificate is different/unavailable. |
| F: final signed payload/package | PASS | Non-debuggable versionCode2 APK, 62,314 bytes; v2/v3 signature and pinned public certificate verify. package_candidate.py --verify passed exact rebuilt ZIP payload, assets, source digest, checksum and manifest. Source dbebef9; SHA-256 cf09e92086d5048774b5e453060adfb8988fe4a236f506ee663aad99420a0119. |
| F: higher-version same-key build | PASS | Built temporary versionCode3 release and signed with the permanent 3072-bit key; v2/v3 signatures verify and fingerprint matches release.json. Final candidate retains versionCode2. Build/static evidence only; no on-phone upgrade claim. |
| E: custom hardware control | N/A | Educational app; no motor/aircraft/custom control outputs. |
| E: Android physical install/lifecycle/update | BLOCKED | No Android phone attached. Run docs/TESTING.md. |
| Content: independent faculty audit | BLOCKED | Source/self-review and arithmetic fixtures only; full TOS coverage incomplete. |
| D: production HTTPS account API | NOT TESTED | No hosted endpoint provisioned; offline accounts are local until explicitly connected/synced. |
| D: live Gemini | BLOCKED | No real key supplied. Provider paths mocked; actual access/quota/usefulness unvalidated. |
| Stable promotion | BLOCKED | Physical Android and faculty gates remain outstanding. |

Source-only checks do not publish a disposable debug APK. The prepared signed APK must pass CI rebuilding, exact ZIP payload comparison (except VCS metadata), certificate/package/version/checksum/asset/source-digest checks before prerelease publication. Public reports/certificate accompany it; private signer never enters GitHub or APK.

Release gate correction: the first remote package check failed because the verifier excluded a guessed VCS ZIP path. A clean local rebuild proved the only differing entry was AGP META-INF/version-control-info.textproto (source S versus later artifact commit). The verifier now excludes that exact non-executable metadata entry, strictly validates its schema and requires its revision to match the manifest source commit. All executable/resource/asset bytes remain compared exactly; regression tests cover changed code/resource rejection and malformed metadata. No APK bytes or signer were replaced for this correction.
