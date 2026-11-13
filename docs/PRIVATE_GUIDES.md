# Private guide imports · v0.4

The user supplied the 2019 Airframe and 2018 Powerplant PDFs and requested IN
banks. Original book content and derived banks stay private. Public git contains
the importer, synthetic tests and app changes; public APKs contain only the 360
original AI foundation items. A separate same-signer private APK contains both.

| Uploaded guide | Source questions | Included IN | Held |
| --- | ---: | ---: | ---: |
| Airframe 2019 | 1,059 | 1,011 | 48 |
| Powerplant 2018 | 1,011 | 992 | 19 |
| Total | 2,070 | 2,003 | 67 |

| AE Prepware subject | IN items |
| --- | ---: |
| Mathematics | 0 |
| Aerodynamics | 77 |
| Structures & design | 146 |
| Construction & repair | 788 |
| Power plant | 992 |
| Economics, laws & ethics | 0 |

Chapter-based subject mapping remains pending faculty/TOS review. IN labels mean
uploaded content, not a claim that the user authored the books. The original
A-C choices are preserved; there is no fabricated D. Printed keys and original
explanations are retained with PDF page, source question, key-page and file hash.
`source-key-verified` explicitly differs from faculty approval. Historical FAA
material does not establish current Philippine rules or complete exam coverage.

The importer detects mirrored text columns, uses italic explanation typography,
checks printed footer keys, and holds unknown/X/conflicting keys, missing choices,
incomplete text, duplicates, and figure/chart references. 61 held items reference
figures/charts and 6 additional items require text/key repair. Reasons can overlap.
The private review queue retains the held records for manual review. Source PDFs
are unchanged. No live AI generates, fills or silently corrects missing content.

Authoring environment: `pip install -r scripts/requirements-authoring.lock`.

```sh
python scripts/import_private_guides.py --airframe /private/airframe.pdf \
  --powerplant /private/powerplant.pdf --output-dir private-study
./gradlew :app:assembleRelease -PprivateBankFile=private-study/AE-IN-private-bank.json
```

Use the permanent signer and `package_private_candidate.py` for a private build.
The script checks signature, manifest, complete unsigned payload, each asset,
source commit, bank checksum and audit counts. It refuses public release paths.
The public candidate verifier rejects any private-study bank. Private outputs
are excluded from git and delivered directly to the user.

Private banks are persisted in IndexedDB per profile so a later public app update
can retain existing IN IDs and progress without exhausting localStorage. Legacy
localStorage banks remain readable. JSON file import/export now allows up to
8 MB; the question count remains bounded at 3,000 including retired revisions.
Export both the bank and progress before reinstalling, clearing data or changing
phones. Import the bank first, then restore its matching progress backup.
A matching hosted account API must use the same private bank; none is deployed
by this change. Offline IN/Hybrid study requires no service.

VersionCode 4 and the existing certificate allow an in-place update from v0.2/
v0.3. Physical installation, system-bar/keyboard behavior, lifecycle and upgrade
need device confirmation; browser/layout/build evidence does not replace it.
