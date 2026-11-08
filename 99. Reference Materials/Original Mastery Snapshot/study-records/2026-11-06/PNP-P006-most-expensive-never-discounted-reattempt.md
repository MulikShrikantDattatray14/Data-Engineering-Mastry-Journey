# PNP P006 — Most expensive products that are never discounted — CLOSED

**Date:** 2026-11-06 (Asia/Kolkata)  
**Result:** Independently corrected SQLite reattempt, **6/6 verified baseline source reattempts**. Original PNP P006 was previously solved (2026-10-27): this is a review, not a newly solved source ID.

## Problem / expected result

Return up to 10 highest-sale-price products sold without discount, excluding products with unknown Sale_Price or Market_Price. Output columns in order: ProductID, Product, Brand, Sale_Price, Market_Price, discount_display, showing 'Full price'. Sort Sale_Price DESC then ProductID ASC. A zero discount is conceptually represented as SQL NULL in a discount calculation; do not confuse actual SQL NULL with the text 'NULL'.

Sample Products: (1,Mug,Home,100,100), (2,Lamp,Home,150,150), (3,Mystery,Home,NULL,100), (4,Bottle,Home,90,100). Expected sample rows: 2 Lamp, then 1 Mug, both 'Full price'.

## First attempt (learner-authored, verbatim)

```sql
select ProductID, Product, Brand, Sale_Price, Market_Price, 
(case
when Market_Price - Sale_Price =0 then 'NULL'
when Market_Price = Sale_Price then 'Full price'

end) as discount_display.
from Products
where Market_Price is not null and  Sale_Price is not null

order by Sale_Price desc , ProductID asc
limit 10
```

**Review:** Invalid dot after alias; string 'NULL' is not SQL NULL and first CASE branch consumes equal-price rows; discounted products not excluded.

## Second attempt (learner-authored, verbatim)

```sql
select ProductID, Product, Brand, Sale_Price, Market_Price, 
(case

when Market_Price = Sale_Price then 'Full price'

end) as discount_display.
from Products
where Market_Price is not null and  Sale_Price is not null

order by Sale_Price desc , ProductID asc
limit 10
```

**Review:** Alias dot syntax error still present. Without it, Bottle (discounted) would incorrectly appear. The assistant explained that CASE controls display while WHERE controls included rows.

## Final independent submission — exact learner query

```sql
SELECT ProductID, Product, Brand, Sale_Price, Market_Price,
    CASE
        WHEN Market_Price = Sale_Price THEN 'Full price'
    END AS discount_display
FROM Products
WHERE Market_Price IS NOT NULL
  AND Sale_Price IS NOT NULL and Market_Price - Sale_Price ==0
ORDER BY Sale_Price DESC, ProductID ASC
LIMIT 10;
```

**Outcome:** Correct for the source's requested output. SQLite `==` is a supported equality operator (standard SQL typically uses `=`). Equal nonmissing prices imply a zero discount, and thus all returned rows display Full price. The solution does not explicitly construct an intermediate nullable discount column, but directly implements its required zero-discount result.

## Executed verification — SQLite 3.46.1

Using a real in-memory SQLite `Products` table:

- Four-row source sample: EXACT expected two rows, order **Lamp** (150) then **Mug** (100), six columns, both 'Full price'.
- Extended 18-product fixture: 10 returned, all equal Sale_Price and Market_Price, sorted Sale_Price descending, ProductID ascending for the two 200-price ties.
- Null-price products excluded, discounted Bottle and expensive discounted product excluded, max 10 enforced.
- Extended ordered ProductID results: **6, 7, 8, 9, 10, 11, 12, 2, 13, 14**.
- Original first/second attempts were reviewed but not independently correct; **final independently authored correction executed and passed**.
- No claim of SQL Server runtime execution.
- Focus minutes: unlogged. New learning reflection: not yet collected; do not invent it.

**Formal status:** CLOSED. Previously solved PNP reattempt minimum target completed: **P001–P006 (6/6)**. No new PNP source IDs credited.

Mirror: [Journey](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/study-records/2026-11-06/PNP-P006-most-expensive-never-discounted-reattempt.md) · [Mastry](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/PNP-P006-most-expensive-never-discounted-reattempt.md).
