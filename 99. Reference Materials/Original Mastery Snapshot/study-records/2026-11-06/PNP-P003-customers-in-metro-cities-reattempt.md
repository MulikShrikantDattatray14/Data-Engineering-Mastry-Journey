# PNP P003 — Customers in metro cities (Day 1 independent SQL reattempt 3)

**Date:** November 6, 2026 (Asia/Kolkata) · **Status:** Not attempted in this session.  
**Origin:** PNP P003, previously solved on October 27, 2026; this is a *source reattempt*, not a new source completion.  
**Existing source file with earlier solutions (DO NOT OPEN until after your own attempt):** [PNP P003 source record](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/1.%20SQL%20Mastery/1.%20SQL%20Mastry/2.PNP-%20foundations%20and%20practice/1.%20Intro%20to%20SQL%20and%20Advanced%20Select/P003.%20Customers%20in%20metro%20cities.md).

## Independent problem summary (no solution spoilers)

A delivery launch team wants a customer list for the five metro areas Bengaluru, Mumbai, Delhi, Hyderabad and Chennai. Select customers whose entered city belongs to one of those metro areas **ignoring capitalization and extra spaces around the name**.

The provided dataset recognizes alternative spellings `Bangalore` for Bengaluru, `Bombay` for Mumbai, and `New Delhi` for Delhi. Treat these as valid matches too.

Return exactly `CustomerID`, `FirstName`, `LastName`, `City`, `State`, in that order. Display `City` with only the *surrounding spaces removed*, preserving its original letter case. Order by **city name alphabetically without case affecting the comparison**, then by `CustomerID` ascending for ties. Do not change spelling variants in displayed output.

## Sample input — Customers

Illustrative nine-row sample from the existing P003 source record, not the full commerce dataset.

| CustomerID | FirstName | LastName | City (literal text) | State |
|---:|---|---|---|---|
| 12 | Asha | Rao | `' Bengaluru '` | Karnataka |
| 5 | Nisha | Shah | `'MUMBAI'` | Maharashtra |
| 21 | Riya | Patil | `'Pune'` | Maharashtra |
| 3 | Dev | Kumar | `'Delhi'` | Delhi |
| 7 | Mira | Das | `'Bengaluru'` | Karnataka |
| 9 | Farah | Ali | `' Chennai '` | Tamil Nadu |
| 14 | Isha | Kumar | `'Bangalore'` | Karnataka |
| 6 | Omar | Khan | `' Bombay '` | Maharashtra |
| 8 | Lea | Singh | `'New Delhi'` | Delhi |

## Expected output

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

## Expected output explanation (no SQL)

- **Isha (14)**: `Bangalore` is an accepted alternative spelling for Bengaluru, so she is included. Alphabetically, `Bangalore` sorts ahead of `Bengaluru`.
- **Mira (7)** and **Asha (12)**: Both are in Bengaluru. Asha's surrounding spaces are removed for display; their cities then tie, so CustomerID 7 appears before 12.
- **Omar (6)**: `' Bombay '` names Mumbai; surrounding spaces are removed and `Bombay` is displayed as entered.
- **Farah (9)**: `' Chennai '` becomes `Chennai` and is included.
- **Dev (3)**: Delhi is a target metro; his record is included.
- **Nisha (5)**: `MUMBAI` matches Mumbai regardless of letter case, while retaining uppercase in the output.
- **Lea (8)**: `New Delhi` is an accepted alternative for Delhi and is included.
- **Riya (21)**: Pune is not among the five metro areas, so she is excluded.

Eight customer rows are expected in exact five-column order; output city values are trimmed but not renamed or recased. Different original city spellings are kept distinct in display/sorting.

## Learner solution and review — pending

- Step 1 reasoning: Pending.
- Learner's original SQLite code and all subsequent versions (verbatim): Not yet submitted.
- Actual SQLite results and errors: Not yet executed.
- Assistant-reviewed SQLite reference: **Withheld until independent learner attempt.**
- Assistant-converted SQL Server/T-SQL reference: **Withheld until after the attempt.**
- Original source provider answer: Stored in P003 source record, **not reproduced now**.
- Learner's optional new-learning Yes/No: Pending.
- Question-closing commits in both repositories: Pending.
- Newly credited PNP source completion: None (P003 was already included in the 20-question baseline).

## Mirrored record links

[Journey P003 reattempt](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/study-records/2026-11-06/PNP-P003-customers-in-metro-cities-reattempt.md) · [Mastry P003 reattempt](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/PNP-P003-customers-in-metro-cities-reattempt.md).


## Third independent attempt — executed SQLite output

Student's exact query:

```sql
select `CustomerID`, `FirstName`, `LastName`, trim(City), `State`
from Customers
where lower(trim(City)) in  ('bangalore','bengaluru','bombay','mumbai','new delhi','delhi','chennai','hyderabad')
order by trim(City) asc , CustomerID asc
```

SQLite 3.46.1 on the nine sample customers returned 8 rows (ID order 14,7,12,6,9,3,5,8), matching expected values and observed row order. The actual fourth column name is `trim(City)`, not `City`. Sorting by `trim(City)` is case-sensitive by default and does not guarantee the requested case-insensitive behavior for new input. Student must independently correct both remaining requirements. No verified P003 reattempt credit yet.


## Step 4 — Identical final-shaped submission, no correction

**Exact learner query (verbatim):**

```sql
select `CustomerID`, `FirstName`, `LastName`, trim(City), `State`
from Customers
where lower(trim(City)) in  ('bangalore','bengaluru','bombay','mumbai','new delhi','delhi','chennai','hyderabad')
order by trim(City) asc , CustomerID asc
```

**Actual execution:** SQLite 3.46.1 in memory against the nine-row illustrative Customers fixture. The query executes without error and returns eight rows in customer ID order: 14, 7, 12, 6, 9, 3, 5, 8. Actual column names: `CustomerID`, `FirstName`, `LastName`, `trim(City)`, `State`. All row values match the eight-row expected output on this particular fixture.

**Review:** This submitted SQL is unchanged from the learner's third attempt. The fourth output heading still fails the required `City` alias. The ordering is on case-sensitive `trim(City)` rather than normalized case-insensitive city, so the sorting contract is not robust despite matching this fixture's observed order. Independent correction pending, no P003 reattempt completion credit. Previous student attempts are retained separately. No full reference SQL is revealed.


## Step 5 — Learner's independently corrected final SQLite (verified)

**Exact final learner submission (verbatim):**

```sql
select `CustomerID`, `FirstName`, `LastName`, trim(City) as City, `State`
from Customers
where lower(trim(City)) in  ('bangalore','bengaluru','bombay','mumbai','new delhi','delhi','chennai','hyderabad')
order by lower(trim(City)) asc , CustomerID asc
```

**Execution:** Executed exactly as submitted in Python `sqlite3` **SQLite 3.46.1**, in-memory, against the 9-row illustrative `Customers` fixture in this record. No error.

**Actual output, complete (8 rows / 5 correctly named columns):**

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

**Exact expected-vs-actual comparison:** PASS — every row and value, 5 exact column names and order, correct exclusion of Pune, inclusive metro spelling variants, preserved original capitalization, trimmed display, case-insensitive city ordering and ascending CustomerID tie-break.

**Independent debugging history:** First learner query produced zero rows because `UPPER(TRIM(City))` was compared with lowercase/mixed-case literals; metro spellings were missing. Second corrected the comparison case but omitted Chennai/Hyderabad and alias/sort requirements (7 rows). Third added the two metros (8 rows), but still lacked the `City` alias and normalized sorting. The next resubmission was identical. **This independently authored final revision** added `AS City` and `ORDER BY LOWER(TRIM(City)) ASC, CustomerID ASC`. Not correct on the first attempt.

## Detailed post-attempt review — progressively executed reference

**Exact reproducible SQLite fixture:**

```sql
CREATE TABLE Customers (
    CustomerID INTEGER, FirstName TEXT, LastName TEXT, City TEXT, State TEXT
);
INSERT INTO Customers VALUES
(12,'Asha','Rao',' Bengaluru ','Karnataka'),
(5,'Nisha','Shah','MUMBAI','Maharashtra'),
(21,'Riya','Patil','Pune','Maharashtra'),
(3,'Dev','Kumar','Delhi','Delhi'),
(7,'Mira','Das','Bengaluru','Karnataka'),
(9,'Farah','Ali',' Chennai ','Tamil Nadu'),
(14,'Isha','Kumar','Bangalore','Karnataka'),
(6,'Omar','Khan',' Bombay ','Maharashtra'),
(8,'Lea','Singh','New Delhi','Delhi');
```

### Stage A — compare entered, cleaned and normalized city (executed)

```sql
SELECT CustomerID, City AS entered_city, TRIM(City) AS cleaned_city,
       LOWER(TRIM(City)) AS normalized_city
FROM Customers ORDER BY CustomerID;
```

| CustomerID | entered_city | cleaned_city | normalized_city |
|---:|---|---|---|
| 3 | Delhi | Delhi | delhi |
| 5 | MUMBAI | MUMBAI | mumbai |
| 6 | `' Bombay '` | Bombay | bombay |
| 7 | Bengaluru | Bengaluru | bengaluru |
| 8 | New Delhi | New Delhi | new delhi |
| 9 | `' Chennai '` | Chennai | chennai |
| 12 | `' Bengaluru '` | Bengaluru | bengaluru |
| 14 | Bangalore | Bangalore | bangalore |
| 21 | Pune | Pune | pune |

**Why:** `TRIM` removes surrounding ordinary spaces, while `LOWER` produces a comparison key. Neither changes the stored `City`. We display the cleaned value but use the normalized value when matching and sorting.

### Stage B — keep accepted metro spellings (executed)

```sql
SELECT CustomerID, TRIM(City) AS City FROM Customers
WHERE LOWER(TRIM(City)) IN
 ('bangalore','bengaluru','bombay','mumbai','new delhi','delhi','chennai','hyderabad')
ORDER BY CustomerID;
```

| CustomerID | City |
|---:|---|
| 3 | Delhi |
| 5 | MUMBAI |
| 6 | Bombay |
| 7 | Bengaluru |
| 8 | New Delhi |
| 9 | Chennai |
| 12 | Bengaluru |
| 14 | Bangalore |

**Why:** The target is eight *allowed spellings* covering five metro areas. Pune is excluded; no Hyderabad row happens to exist in this sample, but Hyderabad is still a required accepted value.

### Stage C — return required columns and deterministic case-insensitive sort (executed)

**Learner's final submission** above was executed and returned the exact expected eight rows, in the required order. The sort key is `LOWER(TRIM(City))`, with `CustomerID` ascending as a tie-break for Bengaluru IDs 7 and 12.

**Pitfalls:** `TRIM(City)` without `AS City` returns an expression-derived column name; `ORDER BY TRIM(City)` may sort capitalized variants differently under case-sensitive collations; `UPPER(...)` compared with lowercase literals yields no matches in default SQLite. SQL does not automatically group synonyms like Bombay and Mumbai unless those spellings appear in the accepted list or a mapping table is used. In production, a normalized city dimension / alias map is safer than a continually expanding hard-coded list.

## Assistant-reviewed SQLite reference (AFTER learner attempt; not provider-official)

```sql
SELECT CustomerID, FirstName, LastName, TRIM(City) AS City, State
FROM Customers
WHERE LOWER(TRIM(City)) IN
 ('bangalore','bengaluru','bombay','mumbai','new delhi','delhi','chennai','hyderabad')
ORDER BY LOWER(TRIM(City)), CustomerID;
```

Equivalent to the learner's independently executed SQLite solution; the explicit `ASC` is optional as ascending is the default.

## SQL Server / T-SQL assistant reference (NOT executed on SQL Server)

```sql
SELECT CustomerID, FirstName, LastName, TRIM(City) AS City, State
FROM dbo.Customers
WHERE LOWER(TRIM(City)) IN
 ('bangalore','bengaluru','bombay','mumbai','new delhi','delhi','chennai','hyderabad')
ORDER BY LOWER(TRIM(City)) ASC, CustomerID ASC;
```

**Note:** This requires a SQL Server version supporting `TRIM`. `dbo` is an illustrative schema prefix. No T-SQL runtime was used and the assistant version is not attributed to the student.

## Source provider answer — attribution and differences

The existing P003 source file links an instructor answer key. It uses `LOWER(TRIM(City))` for filtering and displays `TRIM(City)`; its sorting is on `TRIM(City)` rather than a fully case-normalized sort. Consequently its ordering is dependent on collation, whereas this independent reattempt's expected output explicitly requires case-insensitive city ordering. The source answer file remains unchanged. Do not confuse a source-labelled official key with a new student attempt or claim that the source key is verified against a different normalization contract.

## Progress and learning capture

- **P003 source reattempt:** Fully and independently corrected on the illustrative SQLite sample; **provisional 3/6 verified reattempts** pending Yes/No learning capture and distinct question-closing commits.
- **Newly solved PNP source IDs today:** 0; P003 already belongs to the previous 20-question solved baseline.
- **First-attempt correctness:** No.
- **Actual study minutes:** Unrecorded.
- **New learning Yes/No:** Pending user response. If Yes, preserve exact wording; if No, record “No new learning” and do not invent a rule.
- **Question-closing checkpoint:** Pending; do not move to P004 before closing.


## Learning capture — No new learning

**Learner's exact response:** `No new learning.`

No new SQL concept is credited or invented. The final SQLite reattempt was independently corrected and verified against the nine-row illustrative sample. P003 was already included in the 20 previously solved PNP questions; it is an independently verified reattempt, not a new source question completion. The formal question-closing checkpoint follows separately.
