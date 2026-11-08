# PNP P002 — Formal closing checkpoint (November 6, 2026)

**Source:** PrepNPlaced P002, Ten highest-priced products · **Type:** Independent reattempt of problem already solved October 26.  
**Result:** Correct on **first independent attempt** using the 13-row illustrative fixture. Exact required 10 rows, four columns and stable ordering verified in SQLite.  
**Learner's learning capture (verbatim):** `No new learning.`

## Complete archived question and evidence

[Full dated P002 problem record, sample input/output and why each row is included, the original student SQL, actual execution, review, progressive explanations, assistant SQLite and T-SQL references](PNP-P002-ten-highest-priced-products-reattempt.md).

### Learner's original SQL (verbatim)

```sql
select ProductID, Product, Brand, Sale_Price
from Products
where Sale_Price is not NULL
order by Sale_Price desc, ProductID asc
limit 10
```

### Actual result in the 13-row illustrative fixture

| ProductID | Product | Brand | Sale_Price |
|---:|---|---|---:|
| 101 | Headphones | Nova | 900 |
| 102 | Tablet | Nova | 800 |
| 103 | Monitor | Pixel | 700 |
| 104 | Keyboard | Typeco | 600 |
| 105 | Speaker | Nova | 500 |
| 106 | Router | Netco | 400 |
| 107 | Camera | Pixel | 300 |
| 108 | Mouse | Typeco | 200 |
| 109 | Lamp | Home | 150 |
| 4 | Mug | Home | 100 |

**Verified:** Exactly 10 rows with the four required columns; the tie on Sale_Price 100 goes to ProductID 4; the zero-priced item remains eligible but ranks outside the top ten; the NULL-price item is excluded.

## Status and integrity

- PNP SQL reattempt progress: **2/6 minimum**, P001 and P002.
- Newly completed PNP source question IDs today: **0** (P002 is part of the old baseline).
- Optional learning: **No new learning.** No revision rule added.
- Full original dataset re-run: **Not claimed**, only the source-record illustrative fixture.
- SQL Server/T-SQL: assistant reference, **not executed** in SQL Server.
- This is a formal question-closing checkpoint committed to the remote default branch of both repositories before P003 begins.

## Cross-repository records

- [Journey P002 record](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/study-records/2026-11-06/PNP-P002-ten-highest-priced-products-reattempt.md)
- [Mastry P002 record](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/PNP-P002-ten-highest-priced-products-reattempt.md)
