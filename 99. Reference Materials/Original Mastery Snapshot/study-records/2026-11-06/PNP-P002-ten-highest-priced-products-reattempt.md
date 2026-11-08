# PNP P002 — Ten highest-priced products (SQL source reattempt 2)

**Study date:** 2026-11-06 (Asia/Kolkata) · **Status:** Pending independent learner attempt.  
**PNP status:** Already solved previously (October 26); new independent *reattempt* pending; no new source-completion credit.  
**Source:** [Original P002 source record](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/1.%20SQL%20Mastery/1.%20SQL%20Mastry/2.PNP-%20foundations%20and%20practice/1.%20Intro%20to%20SQL%20and%20Advanced%20Select/P002.%20Ten%20highest-priced%20products.md). That record contains an earlier student/source answer; **do not consult it during the reattempt**.

## Independently worded problem statement (no answer spoiler)

A merchandising team needs exactly ten product entries for its **Premium Picks** showcase. Select the ten products with the greatest `Sale_Price`, highest price first. Ignore products with a `NULL` price. When two products have the same sale price, use the **smaller `ProductID` first** so the cut-off decision stays stable. A product priced at zero is not automatically invalid (though it may not rank among the top ten).

Return precisely these columns in order: `ProductID`, `Product`, `Brand`, `Sale_Price`.

## Sample input — Products

This **illustrative** sample is from the earlier P002 source record, not a claim about rows in the full PNP commerce dataset.

| ProductID | Product | Brand | Sale_Price |
|---:|---|---|---:|
| 4 | Mug | Home | 100 |
| 20 | Bottle | Home | 100 |
| 30 | Sticker | Home | 0 |
| 31 | Mystery item | Home | NULL |
| 101 | Headphones | Nova | 900 |
| 102 | Tablet | Nova | 800 |
| 103 | Monitor | Pixel | 700 |
| 104 | Keyboard | Typeco | 600 |
| 105 | Speaker | Nova | 500 |
| 106 | Router | Netco | 400 |
| 107 | Camera | Pixel | 300 |
| 108 | Mouse | Typeco | 200 |
| 109 | Lamp | Home | 150 |

## Expected output

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

## Explain each expected row and exclusion (no SQL algorithm)

- **101–109:** Their prices 900, 800, 700, 600, 500, 400, 300, 200 and 150 are the nine highest priced entries in descending order.
- **Product 4 (Mug):** Its price is 100. It takes the **tenth** slot because it ties with Bottle (ProductID 20) but its ID is smaller.
- **Product 20 (Bottle):** Also priced 100, but loses the final-slot tie break to Product 4.
- **Product 30 (Sticker):** Has a legitimate numeric price of 0, but ranks below the top ten, so it is not selected.
- **Product 31 (Mystery item):** Its price is NULL, so it is ineligible.
- Exactly **ten rows**, **four columns** and fixed price/ID ordering are required.

## Learner workspace — withheld until attempt

**Step 1 student reasoning:** Pending.  
**Original independent SQLite submission:** Pending.  
**Actual executed SQLite output/errors:** Pending.  
**Independently corrected learner versions:** Pending.  
**Assistant-reviewed SQLite reference:** Withheld.  
**Assistant-reviewed SQL Server / T-SQL reference:** Withheld.  
**Earlier source key:** Not shown to avoid spoiling the independent reattempt.  
**Optional new learning Yes/No:** Pending.  
**Question closing checkpoint in both repositories:** Pending.

[Learning repository record](https://github.com/MulikShrikantDattatray14/data-engineering-journey/blob/main/study-records/2026-11-06/PNP-P002-ten-highest-priced-products-reattempt.md) · [Mastry mirror](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry/blob/main/study-records/2026-11-06/PNP-P002-ten-highest-priced-products-reattempt.md)


## Learner's first independent submission — SQLite (verbatim)

```sql
select ProductID, Product, Brand, Sale_Price
from Products
where Sale_Price is not NULL
order by Sale_Price desc, ProductID asc
limit 10
```

**Actual execution:** Python sqlite3 SQLite **3.46.1**; in-memory `Products(ProductID, Product, Brand, Sale_Price)` loaded with the 13 example rows given above; SQL was executed exactly as submitted. SQLite returned these exact four columns in the selected order.

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

**Expected versus actual:** The entire ordered list exactly equals the expected 10 rows, 4 columns, all values and sort order. **PASS — correct on first independent reattempt, no SQL changes necessary.** It excludes NULL-priced Product 31, leaves eligible zero-priced Product 30 below the Top 10, and breaks the 100-price tie in favor of ProductID 4 over ProductID 20. This is a reattempt of previously solved source P002, not a newly solved PNP source ID.

## Completed post-attempt walkthrough (assistant-authored)

**SQLite fixture for reproducibility:**
```sql
CREATE TABLE Products(ProductID INTEGER, Product TEXT, Brand TEXT, Sale_Price INTEGER);
INSERT INTO Products VALUES
(4,'Mug','Home',100),(20,'Bottle','Home',100),
(30,'Sticker','Home',0),(31,'Mystery item','Home',NULL),
(101,'Headphones','Nova',900),(102,'Tablet','Nova',800),
(103,'Monitor','Pixel',700),(104,'Keyboard','Typeco',600),
(105,'Speaker','Nova',500),(106,'Router','Netco',400),
(107,'Camera','Pixel',300),(108,'Mouse','Typeco',200),
(109,'Lamp','Home',150);
```

**Stage 1: validate eligible prices.** `Sale_Price IS NOT NULL` retains 12 rows (all except ProductID 31). A zero price stays eligible. The learner's final executed query applies this exact test.

**Stage 2: sort by two keys.** Descending prices determine ranking, and ascending IDs resolve ties. Price 100 appears twice, with product 4 before 20; zero-price product 30 sorts below them. The ordered eligible IDs before limiting are:
`101,102,103,104,105,106,107,108,109,4,20,30`.
This is a logically reconstructed intermediate order from the sample; no separate intermediate-stage execution is claimed.

**Stage 3: take exactly ten after sorting.** The learner's executed final SQLite query returns IDs:
`101,102,103,104,105,106,107,108,109,4`, with the full row values in the actual-output table above. `LIMIT 10` is SQLite syntax; applying `LIMIT` without a stable ORDER BY would not guarantee the intended top ten.

**Common errors and edge cases:** Do not use `Sale_Price > 0` because it excludes genuine zero prices. Do not sort only by price if the tenth place can be tied. `WITH TIES` may produce more than ten records. On very large datasets, verify an index and query plan instead of assuming speed.

## Assistant SQLite reference (reviewed; not the student's code)

```sql
SELECT ProductID, Product, Brand, Sale_Price
FROM Products
WHERE Sale_Price IS NOT NULL
ORDER BY Sale_Price DESC, ProductID ASC
LIMIT 10;
```

This matches the student's independently executed query except for formatting/case. It is an **assistant-reviewed** reference, not a separate official answer key.

## Assistant SQL Server / T-SQL reference (NOT executed in SQL Server)

```sql
SELECT TOP (10) ProductID, Product, Brand, Sale_Price
FROM dbo.Products
WHERE Sale_Price IS NOT NULL
ORDER BY Sale_Price DESC, ProductID ASC;
```

SQLite uses `LIMIT 10`; T-SQL uses `TOP (10)`. `dbo.` is an illustrative SQL Server schema prefix, not proof of the actual source schema. No T-SQL runtime verification is claimed.

## Existing PNP provider answer key — comparison

The original P002 repository file includes the source-labelled instructor query. It uses the same non-NULL price filter, descending price and ascending ProductID tie-break with LIMIT 10. **This is the existing stored source key, not the student's current submission or a newly generated official answer.** The source record remains unchanged.

## Completion gate

- **Source P002 reattempt:** Independently correct on first try; SQLite exact sample verified.
- **New PNP source ID completion:** None (P002 was already in baseline).
- **Learner-identified new learning:** Optional Yes/No not yet asked/recorded.
- **Formal question-closing commits in both repos:** Pending learning capture. Do not move to P003 before closing checkpoint.


## Learning capture — No new learning

**User's exact response:** `No new learning.`

No new concept is credited to the SQL rules bank, and no learner insight is invented. The P002 source reattempt was independently correct on the first submitted query and matched the 13-row illustrative sample's expected 10-row output. It remains an already-solved PNP baseline ID, **not a new source completion**. Formal question-closing checkpoint follows separately.
