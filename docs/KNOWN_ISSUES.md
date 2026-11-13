# Known limitations and outstanding validation

- **Stable promotion blocked:** no physical Android device connected. Installation, System WebView compatibility, background/force-stop, font scale/TalkBack, Storage Access Framework backup/restore, upgrade and real-device timing must be checked using TESTING.md.
- **Content review pending:** 72 source-checked foundation questions; not a complete PRC syllabus/TOS bank. Independent faculty audit and approved content expansion required for course-level reliance.
- **Cohort service included, not hosted:** needs persistent server storage, HTTPS and operator security configuration. Streamlit alone does not host the API. Shared standings are unavailable until an instructor supplies an endpoint.
- **Optional AI untested live:** a configured Gemini key/model and faculty review are needed. Local adaptive practice is rule-based, not an LLM. A local coursework template always works.
- **Ranking is motivational:** offline answer keys are available to users; pseudonyms are unverified; registration can be repeated within bounded limits. No claim of proctoring, anti-cheat or official standings.
- **Candidate signing:** CI debug keys are disposable; future candidate builds may require backup/uninstall. Production signing continuity is not established. No app-store build/publication included.
- **Portable backups:** progress requires the same question bank version. New-bank imports reset local progress after confirmation. No cross-bank migration or anonymous-account token backup/recovery in v0.1.
- **Server scaling:** single SQLite worker and an operator-controlled cohort, not an open large-scale public platform. Deploy behind TLS, capacity/rate limits and backups. No default external API URL or embedded secrets.
