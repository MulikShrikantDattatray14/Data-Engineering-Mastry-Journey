# Day 1 — Slot 03 — SQL — new pending source tasks

**Date:** 2026-11-06 (Asia/Kolkata)  
**Status:** Planned / not yet verified  
**Actual start/end:** Not recorded  
**Target:** Attempt A016/P009/P013/P014 if foundations verified; preserve every query attempt  
**Actual reviewed work:** None verified

## Full theory and lesson content
Not recorded yet. When taught, preserve the original, assistant-authored explanations, diagrams as descriptions, code, outputs, examples and reasoning in teaching order.

## Questions as presented
Not recorded yet. Record original tutor-authored questions faithfully; for PNP/Bosscoder proprietary material, link and summarize the source rather than publicly reproducing entire paid worksheets.

## Your original attempt
Not submitted yet. Store the first SQL/Python code or written answer **unaltered**, even if it is incorrect.

## Review and revised attempt
Pending. Record feedback, tests, complexity, improvements and later revision separately. Do not rewrite the original attempt.

## Revision and mastery
- Concepts independently explained: Not assessed
- Original practice attempted: Not assessed
- Correctness reviewed: Not assessed
- Evidence and source IDs/pages: None yet
- Focus minutes: Not logged
- Topic mastered: Not assessed

[Day 1 index](README.md) · [Study archive policy](../../SESSION-ARCHIVE-POLICY.md)


## Additional guided SQL practice — November 6 session wrap-up

**Session status:** Concluded and reviewed at learner's request. The originally planned new PNP source IDs A016, P009, P013 and P014 were not attempted, so Slot 03's official source target remains outstanding. These three guided challenges are **not** counted as newly completed PNP IDs. Database execution was not performed in this chat.

### Guided challenge 1 — Customer email validation

User's final reviewed answer:

```sql
SELECT
    CustomerID,
    FirstName,
    LastName,
    Email,
    CASE
        WHEN Email IS NULL
             OR LENGTH(TRIM(Email)) = 0
            THEN 'Missing'
        WHEN Email LIKE '% %'
            THEN 'Contains a space'
        WHEN Email NOT LIKE '%_@_%._%'
            THEN 'Invalid format'
        ELSE 'Valid'
    END AS issue
FROM Customers
WHERE Email IS NULL
   OR LENGTH(TRIM(Email)) = 0
   OR Email LIKE '% %'
   OR Email NOT LIKE '%_@_%._%'
ORDER BY CustomerID ASC;
```

**Review:** Correct for the specified *basic* LIKE format check; the initial mistake was an extra literal `*` in the LIKE pattern. SQL LIKE does not provide strict email-address validation. This resembles the pending P004 reattempt, but is logged as chat-reviewed, not separately database-executed or formal source-closed.

### Guided challenge 2 — Duplicate emails

**First learner attempt (exact SQL):**

```sql
select Email, count(CustomerID) as DuplicateCount
from Customers
where Email is not null 
group by Email
order by DuplicateCount desc
```

**Feedback:** Missing HAVING; query included email addresses occurring only once.

**Learner's corrected query (exact SQL):**

```sql
select Email, count(CustomerID) as DuplicateCount
from Customers
where Email is not null 
group by Email
having count(CustomerID) >=2
order by DuplicateCount desc
```

**Review:** Correct; WHERE filters rows and HAVING filters aggregated groups.

### Guided challenge 3 — Customer records sharing duplicate emails

**First learner attempt (exact SQL):**

```sql
SELECT CustomerID, FirstName, Email,
      
FROM Customers
WHERE Email IS NOT NULL
GROUP BY Email
HAVING COUNT(CustomerID) >= 2
ORDER BY  COUNT(CustomerID)  DESC;
```

**Feedback:** Extra SELECT comma; nonaggregated columns with GROUP BY Email; grouped output cannot return all customer rows.

**Second learner attempt (exact SQL):**

```sql
SELECT CustomerID, FirstName, Email
FROM Customers
WHERE Email IN (
    SELECT Email,
       
FROM Customers
WHERE Email IS NOT NULL
GROUP BY Email
HAVING COUNT(CustomerID) >= 2

)
ORDER BY CustomerID ASC;
```

**Feedback:** Correct subquery design, extra trailing comma in inner SELECT.

**Reviewed reference after syntax correction (assistant-edited):**

```sql
SELECT CustomerID, FirstName, Email
FROM Customers
WHERE Email IN (
    SELECT Email
    FROM Customers
    WHERE Email IS NOT NULL
    GROUP BY Email
    HAVING COUNT(CustomerID) >= 2
)
ORDER BY CustomerID ASC;
```

**Review:** Correct for the stated requirements. IN handles a multi-row set of duplicate email addresses. Final syntactically corrected text was presented by the assistant, not separately re-submitted by the learner.

**Handoff:** Guided SQL portion complete for this study session; next independent work is Python. Remaining PNP SQL source/stretch questions and unverified practice should remain visible in the tracker.
