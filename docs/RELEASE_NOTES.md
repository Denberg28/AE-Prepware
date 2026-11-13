AE Prepware 0.1.0-rc.1 — Android test candidate

Offline quizzes with 72 original foundation questions, explanations and references; adaptive study, weighted short checks, progress, bookmarks, mistakes, daily quests, backup/recovery and opt-in cohort challenges. Optional Python API and private Streamlit faculty coursework/review dashboard included in source.

Android 8.0+ with an updated System WebView. Install the Test-Candidate.apk; export progress before uninstalling or changing signer. Debug-signed for controlled testing, not production or Play Store distribution. Source commit, signature and SHA-256 are recorded in accompanying files. Future clean candidate builds may use a different debug signer; backup/uninstall/reinstall may be needed.

Validated: automated question/core/API tests, desktop-browser study/recovery flow, Android assemble and lint, APK manifest/signature/size checks. These do not establish physical-device performance or independent educational correctness.

Outstanding: physical Android install/lifecycle/document-picker/upgrade tests; independent faculty question audit; production HTTPS cohort deployment; live optional AI-provider verification. The foundation bank is not full PRC syllabus coverage. No official affiliation or pass guarantee. See docs/TESTING.md for the runnable phone procedure and docs/KNOWN_ISSUES.md for limits.
