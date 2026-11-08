# Q8 — Final question-closing checkpoint

**Date:** 2026-11-06 (Asia/Kolkata)  
**Question:** Tutor-created Q8 — Vendors Without Qualifying Deliveries  
**Review outcome:** CLOSED — independent learner correction successfully verified in SQLite. **Not first try.** Not a PNP course source completion. A single corrected fixture does not prove general mastery.

## Learning evidence

**[Full Q8 question, input, expected output, every original learner SQL step/error, actual outputs, detailed progressive SQLite and T-SQL review](Q8-vendors-without-qualifying-deliveries.md)**

### Learner's final SQLite query — exact original text

```sql
select v.vendor_id, v.vendor_name, v.region
from vendors as v
left join deliveries as d on v.vendor_id=d.vendor_id and d.status='delivered' and d.amount > 1000 and (v.region = 'West' or d.service='express')
where d.vendor_id is null
order by v.vendor_id asc
```

**SQLite actual / expected (exact match):**

| vendor_id | vendor_name | region |
|---:|---|---|
| 1 | Atlas | West |
| 2 | Birch | North |
| 4 | Drift | South |
| 5 | Ember | North |
| 8 | Haven | East |

**Verification:** 5 rows, 3 columns, vendor ID ascending, zero duplicates, all right vendors and actual left-table IDs. The learner independently corrected earlier ambiguous column, trailing comma and NULL `d.vendor_id` projection/sorting errors.

**Learner answered Yes to "Did you learn anything new?" Their exact insight:**

```text
anti join pattern concept
```

This is the learner's verbatim insight; technical commentary and SQLite/T-SQL reference queries are assistant authored. The assistant's SQLite alternative with `d.delivery_id IS NULL` was also independently run, giving the same five rows. The SQL Server/T-SQL reference is supplied but **not executed** in SQL Server; no third-party official answer exists for the tutor-created diagnostic.

## Cross-repository and progress integrity

- [Learning repository Q8 record](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/study-records/2026-11-06/Q8-vendors-without-qualifying-deliveries.md)
- [Data Engineering Mastry Q8 mirror](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/Q8-vendors-without-qualifying-deliveries.md)
- [SQL-R007 in learned rules](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/01-sql/revision/LEARNED-RULES-AND-SYNTAX.md#sql-r007--q8-anti-join-transfer-and-selecting-left-side-ids)
- [Day 1 revision index](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/10-learning-journal/sessions/2026-11-06/PRACTICE-INDEX.md)
- [Day 1 Slot 1 journal](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/10-learning-journal/sessions/2026-11-06/slot-01-sql.md)
- [Progress JSON](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/progress/daily-progress.json): 8/8 tutor questions reviewed, 4 independently correct/corrected, one first-try correct; zero newly completed PNP SQL source questions or verified Python PDF pages; no focus minutes invented.

**After Q8:** Continue the planned PNP SQL source reattempts and independent Q3–Q6 retries. Preserve the question-first record workflow across both repositories. This file is the distinct formal question-closing remote commit checkpoint.
