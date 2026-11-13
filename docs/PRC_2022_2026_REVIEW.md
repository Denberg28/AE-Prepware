# AE Prepware — PRC bank review, 2022–2026

Review completed 14 November 2026 (Philippine time). Research downloads are dated 13 November UTC. Candidate: 0.6.0-rc.1. This is an independent study-bank audit, not PRC endorsement or a validated minimum preparation syllabus.

## Evidence and limits

The five completed regular examination cycles reviewed are 2022, 2023, 2024, 2025 and 2026. Official examination programs for all five years were located and checked. All use the same six subject weights. Resolution 04 (2026) changes the first-day subject order, placing Mathematics before Aerodynamics. It cites the 2010 table of specifications (TOS); the detailed TOS on PRC's board page is the principal competency map used here.

An authenticated, complete, publicly released set of five years of actual examination papers and answer keys was not found. Consequently, this review cannot measure past-paper frequency, predict repeated questions, establish an optimal minimum bank size, or estimate a passing probability. Search-discovered recollections, third-party uploads and pre-board papers were not treated as official questions, copied into the scored bank, or used to assert recurrence. Results announcements establish examination cycles, not topic frequencies.

Official source links:

- [2022 revised program](https://www.prc.gov.ph/sites/default/files/120122%20revised%20exam%20program%20dec%202022%20aele%20%28aero%20engg%29.pdf).
- [2023 revised program](https://www.prc.gov.ph/sites/default/files/revised%20exam%20program%20dec%202023%20%28aero%20engg%29.pdf).
- [2024 program](https://www.prc.gov.ph/sites/default/files/exam%20program%20DEC%202024%20%28aero%291.pdf).
- [2025 program, within PRC Cebu advisory](https://www.prc.gov.ph/sites/default/files/revised%20ra%20aero%2012-2025%20ro7%20cebu.pdf); only program content was used.
- [2026 program](https://www.prc.gov.ph/sites/default/files/exam%20program%20nov%202026%20%28aero%29.pdf).
- [Resolution 04, 2026](https://www.prc.gov.ph/sites/default/files/PRB-AeronauticalEngineer-BoardReso-2026-04.pdf).
- [Detailed TOS, Resolution 01, 2010, pages 3–9](https://www.prc.gov.ph/sites/default/files/TOS%20AERO%202010-01.pdf).
- [PRC syllabus](https://www.prc.gov.ph/sites/default/files/Board%20of%20Aeronautical%20Engineering%20-%20Syllabi_0.pdf) and [board source index](https://prc.gov.ph/Pages/PRBv4/AeronauticalEngineering.htm).
- [2026 official results announcement](https://www.prc.gov.ph/article/november-2026-aeronautical-engineers-computer-based-licensure-examination-results-released).

Exact downloaded PDF hashes and URLs are in `prc-research-sources.json`. The 2010 TOS was rendered and read from its scanned pages. The shorter syllabus download omits Power Plant detail; the TOS and current program supply it. The TOS's printed item counts are recorded directly; they are not recalculated from rounded percentages.

## Findings and the compact core

The original public bank has 360 AI foundation records. Much of its volume comes from eight calculation families with six parameter sets per subject; Construction also contains conceptual items. These are useful foundations, but their count greatly overstates distinct competency coverage. All 264 parameterized calculations were recomputed from the printed givens without importing the generator. In addition, 77 selected numeric exercises have separately worked expected values. These checks matched. Symbolic/conceptual items were considered during selection; this is not independent faculty approval.

The private bank's 2,003 unique IN source questions come from the uploaded 2018 Powerplant and 2019 Airframe FAA-oriented guides. They emphasize maintenance knowledge and omit Mathematics and Philippine law. Many were classified by chapter rather than by PRC competency. Printed-key agreement does not establish technical correctness, current applicability or Philippine jurisdiction.

The new **PRC foundations** set selects **240 existing questions: 120 AI + 120 IN**. The public build contains its 120-item AI subset. The private core reduces the default study workload by about 90% relative to 2,363 original records. This is a practical starter budget, not a proven minimum for board readiness.

| Subject | PRC weight | Core AI | Core IN | Core total |
| --- | ---: | ---: | ---: | ---: |
| Mathematics | 10% | 20 | 0 | 20 |
| Aerodynamics | 25% | 20 | 20 | 40 |
| Structures and Design | 20% | 20 | 3 | 23 |
| Construction, Repair and Modification | 15% | 20 | 37 | 57 |
| Power Plant | 20% | 20 | 60 | 80 |
| Economics, Management, Laws and Ethics | 10% | 20 | 0 | 20 |
| **Total** | **100%** | **120** | **120** | **240** |

Core inventory reflects usable existing material and does not reproduce examination proportions. Use PRC weights to allocate study time; Aerodynamics and Structures need substantial additional work despite smaller available pools. Item-level area assignments and all empty areas are recorded in the selection policy and focus audit. A nonzero area count means some foundation material exists, not that the competency is fully covered.

Core selection favors distinct concepts and applications, excludes most peripheral system-maintenance trivia, and reduces repeated number variants. Selected wood, sheet-metal, materials and repair questions move to Construction; structural configuration items stay in Structures. Two standard-atmosphere questions move from Power Plant to Aerodynamics. Thirty-four corrected-subject copies retain original wording, choices, explanations, provenance and keys. Their old IDs are retired, retained and still grade historical results.

Five additional IN records were retired pending review: a carbon-composite question lacks a fully correct combination option; a center-of-pressure item omits airfoil/range assumptions; a roll item confuses translation and rotation; a piston-speed item needs its kinematic approximation stated; and a combustion item needs ideal-cycle qualification. No replacement answer key was guessed. ST005 is also retired because its stem depends on a preceding question that may not appear in a randomized session. The original 67 figure/ambiguous imports remain held separately; the private review queue now contains 72 entries.

Technical review references include [FAA PHAK](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak), [NASA center of pressure](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/center-of-pressure/), [MIT ideal-cycle analysis](https://ocw.mit.edu/ans7870/16/16.unified/thermoF03/chapter_5.htm), and the original question citations. The piston-speed hold is an engineering-model review finding. Source-key matching for the original 2,003 records is inherited from the earlier Poppler audit; every historical record remains unchanged in grading content, and every subject-correction copy was compared with its original.

## Coverage still requiring approved items

| Priority | Subject | Work required |
| --- | --- | --- |
| 1 | Aerodynamics | Shock/expansion analysis, flight performance and gust calculations, wind-tunnel operation and similarity, atmosphere profiles, buoyancy. |
| 1 | Structures | Indeterminate systems, trusses, gust/maneuver loads, wing/fuselage/gear/mount design and configuration tradeoffs. |
| 1 | Power Plant | Flow/non-flow thermodynamics, integrated performance calculations, pulsejet/ramjet/rocket principles and calculations. |
| 1 | Laws and management | PD 1570 IRR, ethics scenarios, RA 9497/ICAO/current Philippine rules, airline operations, R&D and manufacturing organizations. |
| 2 | Mathematics | Bearings/spherical trigonometry, conics/transforms, advanced ODE/PDE, related rates and aeronautical applications. |
| 2 | Construction | Weight/balance extremes, weighing, hardness/process selection, production QA and Philippine repair authorization. |

Wind tunnels, component design, duct/rocket propulsion and industrial organizations are entire TOS areas with no adequate core coverage. New approved advanced items should replace redundant core exercises while keeping the study set compact. Unreviewed AI drafts were not added to scored practice. Independent faculty review and current Philippine regulatory checking remain necessary before claiming comprehensive board preparation.

## Study and upgrade behavior

The default core drill has 20 distinct questions from one source, or 10 AI + 10 IN in Hybrid. Selection spreads questions across available topics and supports adaptive review. Full bank retains 50-question drills and 25 + 25 Hybrid. Source pools that cannot meet a quota are disabled; the private Structures core has only three IN items, so use its AI core or Full bank. Mathematics and Laws/Ethics have no IN pool.

Use short adaptive drills, read explanations for errors, and revisit weak topics over successive days. Complete advanced coverage from the listed syllabus areas alongside these foundations. Accuracy measures practice performance, including repeated attempts; it is not examination readiness.

Install the permanently signed candidate over v0.2–v0.5 without uninstalling. Export progress and the bank first. A directly compatible bundled refresh validates all old question content and saved progress before persisting the new snapshot. Unrelated/custom banks are retained. Both 20- and 50-item account results can sync to the matching updated service; old queued versions require the service's archived banks. No production service is deployed by this update. Keep separate bank/progress backups before changing phones or downgrading.

Automated content, account, browser and Android checks are recorded with the candidate. Physical Android validation and independent faculty approval remain pending. Uploaded guide content and private review records are excluded from the public repository and public APK.
