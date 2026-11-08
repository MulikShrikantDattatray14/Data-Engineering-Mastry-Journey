# PNP P001 — Brand directory (Day 1 source reattempt 1)

**Date:** 2026-11-06 · **SQL Slot 1** · **Status:** Reattempt pending (no new attempt submitted).  
**Source:** PrepNPlaced P001, previously solved 2026-10-26; this is a **reattempt**, not a new source-problem completion.  
**Original source record:** [P001 in Data Engineering Mastry](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/1.%20SQL%20Mastery/1.%20SQL%20Mastry/2.PNP-%20foundations%20and%20practice/0.%20SQL%20basics/P001.%20Brand%20directory.md).  
**Mirrored learning records:** [Journey](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/study-records/2026-11-06/PNP-P001-brand-directory-reattempt.md) · [Mastry](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/PNP-P001-brand-directory-reattempt.md).

## Problem (independently worded summary of the existing source record)

Create a clean, alphabetically ordered list of **distinct brand names** found in the `Products` table for an e-commerce brand-selection filter. Ignore missing brands, empty strings and entries containing only spaces. Extra spaces around a brand name should not cause it to be treated as a different brand. Return a single column named `Brand`.

The source record contains the whole dataset schema; this reattempt uses the existing record's **illustrative 8-row sample**, rather than asserting those values are from the original dataset.

## Sample input: Products

| ProductID | Brand |
|---:|---|
| 1 | `Nike` |
| 2 | ` Nike ` (one space on both sides) |
| 3 | NULL |
| 4 | `''` (empty string) |
| 5 | `   ` (three spaces) |
| 6 | `Adidas` |
| 7 | `Puma` |
| 8 | `Adidas` |

## Expected output

| Brand |
|---|
| Adidas |
| Nike |
| Puma |

**Why:** The two variants of Nike represent one cleaned name. Adidas appears twice but must be listed once. Product 3 has NULL, 4 is empty, and 5 has only spaces, so none becomes an output entry. Puma is valid. The three remaining names are alphabetically sorted. No algorithm or SQL answer is provided before the independent reattempt.

## Learner-led workspace

**First reasoning:** Pending.  
**Original reattempt SQL submission:** Pending.  
**Actual SQLite output/errors:** Pending.  
**Independent correction:** Pending.  
**Post-attempt assistant SQLite reference:** Withheld.  
**Post-attempt assistant T-SQL reference:** Withheld.  
**Provider's official answer from existing source:** Withheld until after learner submission; do not misattribute the source repository's earlier solution to the current attempt.  
**Progress:** Baseline source P001 already previously solved; no reattempt credit until newly verified.


## Step 1 — learner's original independent SQLite attempt (verbatim)

```sql
select distinct trim(brand) as Brand
from Products
where trim(brand) is not null
order by trim(brand) asc
```

**Executed with SQLite 3.46.1**, in memory, against the eight-row *illustrative* Products fixture documented above. The learner-submitted query ran without syntax errors.

**Actual columns:** `Brand`.

**Actual result, in returned order (4 rows):**

| Brand |
|---|
| `''` (empty string) |
| Adidas |
| Nike |
| Puma |

**Expected (3 rows):**

| Brand |
|---|
| Adidas |
| Nike |
| Puma |

**Review:** `DISTINCT TRIM(brand)` correctly collapses repeated and space-padded brands; `IS NOT NULL` excludes Product 3 but does not exclude `''` or whitespace-only brands because `TRIM('   ')` returns `''`, which is not NULL in SQLite. The two empty cleaned strings become one extraneous output row after DISTINCT. The student independently solved trimming, deduplication and ordering, but the empty-value requirement remains unmet. **No solution or reference answer is revealed.** Ask for a revised SQLite submission that eliminates the empty row while retaining the three expected brands.

**Status:** Attempted; correction pending. Previously solved baseline PNP P001 is unchanged. New verified *reattempt* credit: 0.


## Step 2 — Learner's independently corrected attempt (verbatim)

```sql
select distinct trim(brand) as Brand
from Products
where trim(brand) is not null and length(brand)>0
order by trim(brand) asc
```

**Actual execution:** SQLite 3.46.1 in memory using the exact 8-row illustrative P001 `Products` fixture documented above. SQL ran successfully.

**Actual result (4 rows, `Brand` column):**

| Brand |
|---|
| `''` (empty string) |
| Adidas |
| Nike |
| Puma |

**Expected result (3 rows):**

| Brand |
|---|
| Adidas |
| Nike |
| Puma |

**Why the extra row persists:** `LENGTH(Brand)>0` measures original text. Product 4's empty string has length 0 and is rejected, but Product 5's three-space brand has length 3, passes the WHERE filter, and is then trimmed to the empty string in SELECT. `DISTINCT` leaves one empty output entry. The correct reasoning is to validate the normalized/trimmed value rather than the raw one. No assistant/provider reference solution has been revealed; user needs an independent second correction.

**Per-product validation:**

| ProductID | Brand | LENGTH(Brand) | TRIM(Brand) | LENGTH(TRIM(Brand)) |
|---:|---|---:|---|---:|
| 4 | `''` | 0 | `''` | 0 |
| 5 | `'   '` | 3 | `''` | 0 |

**Progress status:** P001 is still a pending reattempt; 0 verified new PNP reattempts credited at this stage. Original baseline source completion is unchanged.


## Step 3 — Independently corrected final SQLite reattempt (verified)

**Learner's exact third SQL submission (verbatim):**

```sql
select distinct trim(brand) as Brand
from Products
where trim(brand) is not null and length(TRIM(Brand))>0
order by trim(brand) asc
```

**Execution:** Actual Python `sqlite3` SQLite version **3.46.1**, in memory, with exactly the eight illustrative `Products(ProductID, Brand)` rows in this problem record. Query executed without errors.

**Actual result:**

| Brand |
|---|
| Adidas |
| Nike |
| Puma |

**Expected result:** Exactly the same three rows, one column called `Brand`, alphabetical ordering. **PASS.** The query removes NULL, empty and whitespace-only brands; trims leading/trailing whitespace; combines duplicate normalized brand names and sorts correctly.

**Independent debugging:** Initial attempt checked only `TRIM(Brand) IS NOT NULL`, which allowed one empty output entry. The next learner-authored attempt added `LENGTH(Brand)>0`, but the original three-space value still passed. The final learner-authored change to `LENGTH(TRIM(Brand))>0` validates the *cleaned* value and passes. **Not a first-try success.**

## Progressive post-attempt walkthrough (assistant-authored)

**Reusable fixture (SQLite):**

```sql
CREATE TABLE Products (ProductID INTEGER, Brand TEXT);
INSERT INTO Products (ProductID, Brand) VALUES
(1,'Nike'),(2,' Nike '),(3,NULL),(4,''),(5,'   '),
(6,'Adidas'),(7,'Puma'),(8,'Adidas');
```

**Stage A — inspect cleaned values (executed):**

```sql
SELECT ProductID, Brand, TRIM(Brand) AS Clean_Brand,
       LENGTH(TRIM(Brand)) AS Clean_Length
FROM Products
ORDER BY ProductID;
```

| ProductID | Brand | Clean_Brand | Clean_Length |
|---:|---|---|---:|
| 1 | Nike | Nike | 4 |
| 2 | `' Nike '` | Nike | 4 |
| 3 | NULL | NULL | NULL |
| 4 | `''` | `''` | 0 |
| 5 | `'   '` | `''` | 0 |
| 6 | Adidas | Adidas | 6 |
| 7 | Puma | Puma | 4 |
| 8 | Adidas | Adidas | 6 |

**Meaning:** TRIM removes surrounding spaces, but does not turn empty strings into NULL in SQLite. `LENGTH(NULL)` is NULL; `LENGTH('')` is 0.

**Stage B — filter valid normalized values:** `TRIM(Brand) IS NOT NULL AND LENGTH(TRIM(Brand)) > 0` eliminates Products 3, 4 and 5. The five remaining cleaned rows before DISTINCT are `Nike, Nike, Adidas, Puma, Adidas`. (This five-value stage is a direct consequence of the executed fixture; the final learner query was independently executed.)

**Stage C — deduplicate and sort:** DISTINCT produces one row each for `Nike`, `Adidas`, and `Puma`; `ORDER BY TRIM(Brand) ASC` returns `Adidas, Nike, Puma`. The independently executed learner final query proves this output.

**Boundary cases:** A NULL brand is not an empty string; spaces-only become empty under TRIM; duplicates that differ only by surrounding spaces normalize to one name. SQLite `TRIM` by default strips ordinary spaces, not all possible Unicode whitespace. If business rules include tabs or other whitespace characters, define the normalization contract explicitly rather than assuming this query handles every kind. On very large data, function-based predicates and DISTINCT sorting may affect indexes; inspect a query plan before optimizing.

## Assistant-reviewed SQLite reference (not student authored; not an official source key)

```sql
SELECT DISTINCT TRIM(Brand) AS Brand
FROM Products
WHERE LENGTH(TRIM(Brand)) > 0
ORDER BY Brand ASC;
```

Because `LENGTH(NULL)` is NULL and a WHERE keeps only TRUE predicates, the explicit `IS NOT NULL` test in the student's solution is logically optional. Keeping it is valid and clear. **Reference is derived and reviewed**, while the student's own full query above is the directly executed verified submission.

## SQL Server/T-SQL reference (assistant-converted; not executed in SQL Server)

```sql
SELECT DISTINCT TRIM(Brand) AS Brand
FROM dbo.Products
WHERE LEN(TRIM(Brand)) > 0
ORDER BY Brand ASC;
```

In SQL Server, `LEN` is the usual equivalent to the SQLite `LENGTH` check (with its own trailing-space behavior), and `dbo` is illustrative. Requires an SQL Server version supporting `TRIM`; **T-SQL reference has not been executed**.

## Existing source-provided solution — source comparison, not a current learner submission

The already-saved [PNP P001 source record](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/1.%20SQL%20Mastery/1.%20SQL%20Mastry/2.PNP-%20foundations%20and%20practice/0.%20SQL%20basics/P001.%20Brand%20directory.md) labels this provider-key solution:

```sql
SELECT DISTINCT p.Brand
FROM Products AS p
WHERE NULLIF(TRIM(p.Brand), '') IS NOT NULL
ORDER BY p.Brand;
```

**Important qualification:** It filters using cleaned `TRIM(p.Brand)`, but selects raw `p.Brand`. Thus `Nike` and `' Nike '` remain distinct in the illustrative sample: the provider-key SQL **does not produce the same normalized output** as this reattempt's specified example. The original reference is preserved verbatim in its source repo. It is neither silently corrected nor attributed to the learner. The learner's submitted SQL satisfies the current illustrative problem specification.

## Completion and insight capture

- **Current attempt:** Verified correct after independent corrections; **source reattempt P001 = 1/6 minimum** in today's planned reattempt work.
- **New PNP solved source IDs:** Zero (P001 already included in the earlier baseline of 20).
- **First-attempt correctness:** No (this reattempt took 3 submissions).
- **Focus minutes:** Not provided; no time credited.
- **New learning Yes/No:** **Pending learner response.** Preserve any Yes wording exactly, then make the question-closing commits in both repositories before continuing.

### Independent reference-run check

Executed separately in SQLite 3.46.1 against the same 8-row illustrative Products fixture:

- Learner final query: `Adidas`, `Nike`, `Puma` — 3 rows.
- Assistant-reviewed SQLite reference (without redundant `IS NOT NULL`): `Adidas`, `Nike`, `Puma` — 3 rows.
- Existing source-labeled provider key (selects raw `p.Brand`): `' Nike '`, `Adidas`, `Nike`, `Puma` — 4 rows. This confirms the stored source key and the independently worded normalized-output question differ on this deliberately space-padded example. Do not claim that provider's original key satisfies the normalized sample as stated; don't alter the source key.

**Question closure still pending the user's optional Yes/No insight.**


## Learner's optional learning capture — completed

**Prompt:** Did you learn anything new from PNP P001?

**Learner's exact response:** `No new learning.`

**Recorded result:** No newly learned rule is claimed and no extra revision-bank entry is created. The independently corrected third SQLite attempt remains verified. This is one completed **reattempt** of previously solved PNP P001, not a newly completed PNP source ID. The full question, illustrative sample input/output and explanation, verbatim submissions, executed result differences, progressive review, assistant SQLite/T-SQL references and previously saved source-key comparison are preserved above.

**Status:** Reviewed, independently corrected and ready for formal question-closing checkpoint. Further unseen-case practice may strengthen mastery.
