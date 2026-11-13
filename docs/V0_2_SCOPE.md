# AE Prepware 0.2.0-rc.1 scope

Baseline: source 50eb1b3, published 0.1.0-rc.1 candidate. Preserve package ph.diversify.aeprepware, existing question IDs, guest progress and Streamlit Secrets support.

Flow: Subjects → choose one subject tab → 50 distinct randomly ordered bank questions with shuffled A–D answers → answer locks immediately, Correct or correct letter/text shown → optional collapsed Explanation pane → next → score out of 50 saved to account history. Leaving/reopening resumes exactly. Insufficient active items blocks the 50-item session without repeats or invented filler.

Accounts: offline creation generates an account number and high-entropy recovery code. Independent profiles isolate progress/results. Number alone does not authenticate. Recovery code is shown for saving; local verification uses a digest, remote verification uses salted scrypt. Optional HTTPS API registration/login binds the same number, adaptive/AI selection, server-graded results and ranking. Offline results queue for retry-safe sync. Offline backups omit credentials. Shared ranking and device-to-device restore require an operator-hosted API; Streamlit remains faculty UI, not API hosting.

Selection: random is default. Adaptive favors missed/unseen/due items in the chosen subject. Optional server Gemini assistance selects a topic from an allowlist using aggregate learning data; all 50 IDs, keys and explanations remain from the source-checked bank. Provider/config failure falls back to adaptive selection. No AI-generated scored questions.

Content: expand to 60 original foundation items per subject (360 total), including explicitly parameterized calculation variants. Preserve 72 existing IDs/keys. Not a complete board review bank; independent faculty approval remains outstanding.

Signing: user authorizes a persistent release signer replacing disposable candidate signing. Private key is never committed or published. Back up recovery material privately; public certificate and SHA-256 fingerprint accompany the release. Android 8+/SDK35/versionCode2. Prior CI candidate key unavailable: initial reinstall/backup required. Verify later version artifact with the same key; physical installation/update test remains BLOCKED without a phone.

Acceptance: 50 unique same-subject questions; varied sessions and answer order; single credit per answer; correct displayed letter after shuffle; explanations collapsed by default; exact resume; score/history survive restart; account isolation/recovery rejection; server recomputes grades, rejects malformed/foreign results, deduplicates retries and awards unique daily correct points; AI cannot alter keys; offline errors preserve queues; old progress migration; keys excluded from public artifacts; release signature/certificate/version/source payload verified. Candidate only until device/content gates pass.
