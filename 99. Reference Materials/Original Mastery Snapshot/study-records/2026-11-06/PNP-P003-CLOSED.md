# PNP P003 — Formal question-closing checkpoint

**Date:** November 6, 2026 (Asia/Kolkata) · **Source ID:** P003, Customers in metro cities  
**Status:** CLOSED — independently corrected and verified against the illustrative nine-customer SQLite fixture; **not correct on the first attempt**.  
**Learning capture, learner's exact response:** `No new learning.`

## Full study archive

[Complete P003 problem, nine-row sample input, expected eight-row output and explanations, every original student SQLite submission and error/output, independently corrected final, progressive walkthrough, assistant SQLite and unexecuted SQL Server/T-SQL references](PNP-P003-customers-in-metro-cities-reattempt.md).

### Learner's final independently corrected SQLite query (verbatim)

```sql
select `CustomerID`, `FirstName`, `LastName`, trim(City) as City, `State`
from Customers
where lower(trim(City)) in  ('bangalore','bengaluru','bombay','mumbai','new delhi','delhi','chennai','hyderabad')
order by lower(trim(City)) asc , CustomerID asc
```

### Verified actual SQLite result = expected output

| CustomerID | FirstName | LastName | City | State |
|---:|---|---|---|---|
| 14 | Isha | Kumar | Bangalore | Karnataka |
| 7 | Mira | Das | Bengaluru | Karnataka |
| 12 | Asha | Rao | Bengaluru | Karnataka |
| 6 | Omar | Khan | Bombay | Maharashtra |
| 9 | Farah | Ali | Chennai | Tamil Nadu |
| 3 | Dev | Kumar | Delhi | Delhi |
| 5 | Nisha | Shah | MUMBAI | Maharashtra |
| 8 | Lea | Singh | New Delhi | Delhi |

**Verified:** All eight row values, five named columns, trimmed yet original-case city, alternative metro spellings, Pune excluded, normalized ordering and customer-ID tie break. SQLite execution is based on the nine-row **illustrative fixture**, not a claimed full-dataset run.

**Independent correction progression:** Original submission returned 0 rows from mismatched uppercase/lowercase comparison; next revision returned 7, missing Chennai; later revision returned all eight but lacked the `City` alias and case-insensitive sort; one identical resubmission; final independent correction met every requirement.

**Source attribution:** Original PrepNPlaced source answer exists in the existing P003 file. It was not attributed to the student's current attempt. T-SQL assistant reference remains **unexecuted** on SQL Server. No new revision rule is added because the student explicitly said no new learning.

## Completion integrity

- Verified old-source reattempts today: **3/6 minimum** — P001, P002, P003.
- Newly completed PNP source IDs today: **0** (P003 already belonged to previous baseline of 20 solved IDs).
- Optional new learning: **No new learning.**
- Next: P004 — Customer emails that cannot be delivered. Present independently worded question and illustrative sample input/output with explanation; withhold solutions until independent attempt.

## Mirrors

- [Journey full P003 record](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/study-records/2026-11-06/PNP-P003-customers-in-metro-cities-reattempt.md)
- [Mastry full P003 record](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/PNP-P003-customers-in-metro-cities-reattempt.md)

This separate file establishes the formal remotely committed question-closing checkpoint in each repository.
