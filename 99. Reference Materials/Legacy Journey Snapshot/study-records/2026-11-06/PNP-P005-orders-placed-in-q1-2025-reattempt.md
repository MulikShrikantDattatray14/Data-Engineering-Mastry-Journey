# PNP P005 — Orders placed in Q1 2025 — CLOSED

**Date:** 2026-11-06 (Asia/Kolkata)  
**Status:** Independently corrected and executed in SQLite 3.46.1; formally verified previously solved PNP source reattempt **5/6 minimum**.  
**Source:** [PNP Q005 original (contains prior answers)](../../1.%20SQL%20Mastery/1.%20SQL%20Mastry/2.PNP-%20foundations%20and%20practice/1.%20Intro%20to%20SQL%20and%20Advanced%20Select/P005.%20Orders%20placed%20in%20Q1%202025.md) in Data-Engineering-Mastry (source already solved 2026-10-27). This review earns no *new* official source question ID.

## Task (restated independently)

Return the four columns `OrderID`, `CustomerID`, `OrderDate`, `Total_Order_Amount` for all Orders placed in January–March 2025, including timestamped orders throughout March 31; order by `OrderDate` ASC then `OrderID` ASC.

Illustrative sample orders: (1,10,2024-12-31,50), (2,11,2025-01-01,100), (3,12,2025-03-31,200), (4,13,2025-04-01,300). Sample expected output includes OrderID 2 and 3 only.

## Learner attempts and feedback (preserved)

**First learner submission:**

```sql
select `OrderID`, `CustomerID`, `OrderDate`,  `Total_Order_Amount`
from Orders
where OrderDate >= '2025-01-01' and OrderDate<= '2025-03-31'
order by OrderDate asc, OrderID asc
```

**Review:** Date-only sample passes, but `<= '2025-03-31'` excludes timestamp text such as `2025-03-31 10:30:00` and `2025-03-31 23:59:59`.

**Second learner submission:**

```sql
SELECT OrderID, CustomerID, OrderDate, Total_Order_Amount
FROM Orders
WHERE OrderDate >= '2025-01-01'
  AND OrderDate <= '2025-03-31'
ORDER BY OrderDate ASC, OrderID ASC;
```

**Review:** Still excludes later March 31 timestamps.

**Third learner submission:**

```sql
SELECT OrderID, CustomerID, OrderDate, Total_Order_Amount
FROM Orders
WHERE timestamp(OrderDate) >= '2025-01-01'
  AND timestamp(OrderDate) <= '2025-03-31'
ORDER BY OrderDate ASC, OrderID ASC;
```

**Review:** Invalid SQLite `timestamp()` function, and the inclusive upper bound remains unsuitable.

**Final independent learner submission (verbatim):**

```sql
SELECT OrderID, CustomerID, OrderDate, Total_Order_Amount
FROM Orders
WHERE OrderDate >= '2025-01-01'
  AND OrderDate <'2025-04-01'
ORDER BY OrderDate ASC, OrderID ASC;
```

## SQLite execution — actual results

The final learner SQL was executed in Python `sqlite3` **3.46.1** on an in-memory `Orders` table with `OrderDate TEXT` holding consistent ISO-style date/date-time strings.

| OrderID | CustomerID | OrderDate | Total_Order_Amount |
|---:|---:|---|---:|
| 2 | 11 | 2025-01-01 | 100 |
| 8 | 17 | 2025-01-01 00:00:00 | 700 |
| 10 | 19 | 2025-02-10 12:00:00 | 900 |
| 11 | 20 | 2025-02-10 12:00:00 | 950 |
| 3 | 12 | 2025-03-31 | 200 |
| 5 | 14 | 2025-03-31 10:30:00 | 400 |
| 6 | 15 | 2025-03-31 23:59:59 | 500 |

**Checks passed:** Exactly the 4 expected columns; original sample returns only OrderID 2 and 3; Jan 1 and all March 31 times included; prior year-end and April 1 midnight excluded; date ascending and equal timestamps tie-break by OrderID. 7/7 expected qualifying records in the extended fixture.

**Important scope:** This comparison assumes ISO-style strings with consistent date formatting; heterogeneous timezone offsets or date formats require normalization.

## Completion and next action

- **Verified:** Correct after independent revisions and actual SQLite execution.
- **Previously solved PNP reattempts:** **5/6**, P001–P005.
- **Newly completed official PNP source IDs:** **0** (P005 was in prior solved baseline).
- **Focus minutes:** Not logged.
- **New learning reflection:** Not yet asked/recorded; do not invent.
- **Next:** Independently reattempt and verify P006.

Cross-repository mirror: [Journey](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/study-records/2026-11-06/PNP-P005-orders-placed-in-q1-2025-reattempt.md) · [Mastry](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/PNP-P005-orders-placed-in-q1-2025-reattempt.md).
