# Historical Chinook easy Q1–Q5: independent preserved-answer cross-check (PARTIAL)

**14 November 2026.** This bounded audit concerns five *pre-existing* exercises in the original archived `A. PNP easy` directory within the Bosscoder-named SQL tree. It is **not** a new PNP 205-question pass and does not change those questions' 94/205 conservative supplied-key replay count.

## Individually inspected and immutable-source pinned

| Original archived exercise | Git blob SHA-1 | Recorded historical status | Reviewer findings |
|---|---|---|---|
| 1. Countries with at least ten invoices | `7fc848a7bab1d47a84a867dfe9f8917cfcc6aa07` | Solved (recorded) 2026-10-13 | Archived SQLite learner query and archived attributed solution agree for >=10 groups and count-order ties; **both include** a NULL country if ten invoices have no country |
| 2. Top five genres by revenue | `1133845497f01802872fa7a7ff7797d158072080` | Same | On archived eight-line teaching fixture: both give Rock 6, Jazz 4, Classical 3, Pop 3, Blues 2. On synthetic *different IDs with same genre name*, learner groups by GenreId but attributed key groups by Name: learner produces Solo 4, Shared 3, Shared 2; attributed key produces Shared 5, Solo 4. Conditional policy mismatch, **not a verified original Chinook failure** |
| 3. Track count per media type | `d5cc9796cb5992812620af9ac7c9c7acf04c7949` | Same | Teaching fixture: five matching results. On synthetic duplicate MediaType.Name across two IDs, learner groups separately (Same 2, Same 1) while attributed key combines (Same 3); both exclude an empty media type |
| 4. Premium-priced tracks | `3fb69c2e889e17cdee9bfb021074c212b31108b3` | Same | Both saved queries use strict >0.99 and sort equal 1.99 prices by Name; NULL price excluded |
| 5. Distinct billing countries | `a7d795aba6c97b8395ee6b70733d0dddabcd570e` | Same | Both queries return distinct billing countries; synthetic repeated NULLs collapse to one NULL country |

Each full original Markdown statement, saved learner SQLite SQL, recorded SQL Server section, and *attributed archived* official solution were read from the preserved original source tree. The archived solution is **not** independently authenticated against the vendor's official grading service or provider original. Recorded historical learner completion is **preserved provenance**, **not newly independently demonstrated mastery**.

## Executable checks and boundaries

[Read-only source-pinned checker](../scripts/check_bosscoder_chinook_easy_01_05_preserved_answers.py) extracts the literal archived learner SQLite and attributed key SQL from their headings, verifies all five Git blob hashes, and compares their returned rows in eight `unittest` cases. Original locally illustrated invoice/genre/media fixtures and new synthetic boundaries were used. These reviewer-only cases are not the complete Chinook database or its authenticated graded outputs. **CI independently verified for the then-final source+documentation main commit `c903331640b21913f653fbae68e1e475f4483059`: [GitHub Actions run 43574749841](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43574749841) PASSED**, with all **8/8 named Chinook tests** explicitly `ok` in decoded validation logs, **122/122 general and 18/18 native PostgreSQL steps** successful, zero failed/skipped; independently matched run SHA to live main before this ledger clarification. Later documentation commits require their own exact-head CI check; see Issue #1.

The two name-versus-ID grouping differences are conditional on nonunique dimension labels, which may be prohibited by the real Chinook data or assumed business rules; do not rewrite the historical attempt or graded key. NULL country handling likewise requires an explicit source-domain policy. No original archive, learner attempts, canonical notes, or progress files were edited.

**Evidence tiers:** indexed = previously; statements = individually re-read here, not necessarily new unique first-pass coverage; synthetic answer pair replay = only after actual CI log verification; authenticated original official answer verified = **no**; learner independently solved in this run = **no**; mastery awarded = **no**. Issue #1 stays open pending full SQL, mentorship Python, Bosscoder, W3Schools and other DE source parity, licensing/PII and final checks. The separate ChatGPT Library study record remains **UNSYNCED** until independent full-audit signoff and separate post-sync CI.
