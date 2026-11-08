# PNP P001 — Question-closing checkpoint

**Date:** November 6, 2026 (Asia/Kolkata)  
**Source:** PrepNPlaced P001 — Brand directory · **Type:** Reattempt of source problem already solved on 2026-10-26.  
**Outcome:** Independently corrected on learner's third submitted SQLite version; matched all three expected sample brands. **New source completion credit: zero.**  
**Learning capture:** Learner answered **“No new learning.”** No new revision rule is claimed.

## Full question and retained evidence

[Complete P001 dated learning record with independent source summary, sample inputs, expected outputs and explanations; all three verbatim learner submissions; executed outputs and differences; progressive review; separate SQLite and unexecuted SQL Server/T-SQL references; comparison with existing provider-key file](PNP-P001-brand-directory-reattempt.md).

**Original PNP question record:** [PNP P001 in Data-Engineering-Mastry](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/1.%20SQL%20Mastery/1.%20SQL%20Mastry/2.PNP-%20foundations%20and%20practice/0.%20SQL%20basics/P001.%20Brand%20directory.md).

## Learner's final SQLite code — verbatim

```sql
select distinct trim(brand) as Brand
from Products
where trim(brand) is not null and length(TRIM(Brand))>0
order by trim(brand) asc
```

## Independently executed sample output

| Brand |
|---|
| Adidas |
| Nike |
| Puma |

**Verification:** Exactly three expected rows, one `Brand` column, no invalid/duplicate brands, alphabetical ordering. Execution on 8-row illustrative fixture, not the full PNP dataset. Attempt 1 returned an extra empty brand; attempt 2 still returned the empty brand because length was checked on raw input; attempt 3 independently corrected this.

**Source-key nuance:** The original course-file answer selects untrimmed `Brand`, which on this specifically padded sample differs from the normalized-output requirement. The source file was left intact; the full review explains the distinction. Do not attribute assistant-provided references to the learner.

## Verbatim learning selection

```text
No new learning.
```

## Progress integrity

- **PNP source reattempts independently verified today:** 1 of minimum 6 (P001).
- **New PNP source IDs solved today:** 0; pre-existing solved-source baseline is 20, including P001.
- **First-try success for reattempt:** No.
- **Python source pages and actual focus minutes:** No verified credit.
- **Next PNP reattempt:** P002, ten highest-priced products. Present full independently summarized question and illustrative sample I/O before asking for learner reasoning. Keep original source solutions hidden until the learner attempts.

## Mirrored records

- [Journey P001 record](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/study-records/2026-11-06/PNP-P001-brand-directory-reattempt.md)
- [Mastry P001 record](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/PNP-P001-brand-directory-reattempt.md)

This dedicated checkpoint is the formal question-closing remote commit. GitHub connector writes directly to `main` without a separate local push.
