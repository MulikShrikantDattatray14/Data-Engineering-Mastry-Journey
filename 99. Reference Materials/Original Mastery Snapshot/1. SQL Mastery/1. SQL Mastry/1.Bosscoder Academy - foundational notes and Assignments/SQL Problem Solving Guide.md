# SQL Problem Solving Guide

Use this approach across all SQL Mastery sections.

## Foundation notes style

Apply this style to the foundation notes in every current and future section. Use `9. Windowing Functions/0. Foundation Notes.md` as the reference.

- Keep one `0. Foundation Notes.md` in each section, with a clear learning sequence and a linked contents list.
- Cover the section's core concepts and useful variations thoroughly, but keep theory short. Explain necessary theory in plain language.
- Teach through small, coherent examples: state the need, show the SQL, show its output, and explain the result briefly. Reuse the same data where it helps comparison.
- Use compact comparison tables for functions, syntax choices, and common mistakes. Separate optional advanced material from the main learning path.
- Prefer SQLite for executable practice. Label SQL Server and other dialect differences accurately, including version-dependent features that affect learning platforms.
- Include a quick revision sheet or decision table and a short correctness checklist. Provide optional sample-table setup when it makes examples easy to run.
- Preserve useful coverage when updating older notes, check sample arithmetic and query outputs, and distinguish tested queries from syntax reviewed without execution.
- Keep foundation notes separate from numbered question files. Continue the existing learner-first question workflow and save detailed question walkthroughs when finalized.

## Guided practice workflow

Save the short checklist below at the end of every question's **Question and image** section, after the complete prompt, example, explanation, and image, and before **Schema**. Keep the five primary question sections. This applies to all current and future sections.

During live practice, the assistant presents only the current step and one focused prompt. The learner attempts it; the assistant reviews it and gives a targeted hint if needed. Continue to the next step only when the current step is satisfied. Do not give the whole checklist or several future steps together in chat, and do not fill in the learner's answers. Keep live attempts, coaching discussion, and progress in the conversation. After the solution is finalized, save the teaching walkthrough described below.

### Problem solving checklist

1. **Define the output:** state what one result row represents, the required columns, and the ordering.
2. **Understand the inputs:** identify table meanings, keys, relationships, duplicates, and NULLs.
3. **Explain the logic:** describe the steps, calculations, and comparisons in plain English.
4. **Choose SQL operations:** match each step to the SQL operations it needs.
5. **Plan intermediate results:** list the needed columns and what each intermediate row represents.
6. **Build gradually:** write one part, inspect its output, and check row counts after joins.
7. **Verify the answer:** check the sample, duplicates, missing matches, NULLs, arithmetic, boundaries, ties, and sorting.

Work through one step at a time during practice. Complete the current step before moving to the next.

## Detailed solution walkthroughs

For every question in every section, let the learner try first. After they confirm a correct final solution, provide and save a detailed walkthrough even if they solved the problem independently. Preserve their solution logic.

If the learner says they give up and asks for the full explanation, provide the complete walkthrough. A request for one code part stays limited to that part. Save the walkthrough when explicitly requested or after final confirmation.

Use the actual table and column names and one consistent example throughout, preferably the question's supplied sample. For each meaningful step:

1. Explain the requirement and why the SQL operation is needed.
2. Show that part of the query in runnable form.
3. Show the resulting rows or grouped values for the same example.
4. Explain how those results lead to the next step.

Finish with the complete assembled query, its final output, and a manual check of the result. Verify that the example tables and calculations agree with the code. Do not replace the actual schema with unrelated everyday analogies.

Save the walkthrough under `### Step-by-step explanation with one example` inside **My solution — SQLite**, after the final query. Keep the five primary sections, generate the SQL Server equivalent, and retain the existing commit-and-push schedule. Apply this to future completed questions; backfill older walkthroughs when requested.

## Detailed approach

**Decide what your data should look like at each step before writing the query.**

Follow this sequence for every problem:

1. **Define the final output clearly.**

   Complete this sentence: **"One row in my answer represents ___."**

   It could represent an employee, a department, a transaction, or a month. Then identify the required columns, sorting, and any rules for ties.

   This decision guides your entire query.

2. **Understand the input tables.**

   Identify what one row represents in each table, which columns uniquely identify it, and how the tables connect.

   Pay attention to duplicates, missing values, and whether matching records are guaranteed. These details affect which rows your query includes and how many times it counts them.

3. **Write the logic in plain English.**

   Describe the work as small steps, such as:

   ```text
   Get the relevant records.
   Attach the information I need.
   Calculate the required value.
   Keep the qualifying results.
   Arrange the output.
   ```

   Write mathematical formulas separately. For an average or percentage, explicitly identify **the numerator and denominator**. For a comparison, identify **what is being compared with what**.

4. **Choose SQL operations based on what must happen to the rows.**

   | What you need to do | SQL tool to consider |
   |---|---|
   | Attach information from another table | `JOIN` |
   | Keep individual rows meeting a condition | `WHERE` |
   | Assign a value based on conditions | `CASE` |
   | Combine rows into one summary per group | `GROUP BY` with aggregates |
   | Filter calculated group results | `HAVING` |
   | Rank or calculate across rows while keeping individual rows | Window functions |
   | Check whether a related record exists | `EXISTS` / `NOT EXISTS` |
   | Build a result in understandable stages | CTE or subquery |

   **Grouping reduces rows into summaries; window functions retain the individual rows.**

5. **Plan the intermediate results.**

   For each stage, write down the columns you need and what one row represents.

   Every CTE or subquery should have a clear purpose, such as "total per department" or "latest record per employee."

   If you cannot explain what an intermediate result contains, clarify that before adding more SQL.

6. **Build and inspect the query in small pieces.**

   Start with the necessary rows and columns. Add joins, calculations, grouping, and filtering gradually.

   **Inspect the result immediately after a join.** A row matching several records produces several joined rows. That may be required, or it may incorrectly inflate your totals.

   At every step, check: "Are these the rows I expected, and does each row still mean what I think it means?"

7. **Check correctness beyond the sample output.**

   Review these common traps:

   - **Duplicates:** should repeated records count separately?
   - **Missing matches:** must records with no activity still appear?
   - **NULLs:** `COUNT(column)` skips them; `COUNT(*)` counts rows.
   - **Arithmetic:** check parentheses, decimal division, and zero denominators.
   - **Boundaries:** distinguish `>` from `>=`, and check date endpoints.
   - **Ties:** decide whether all tied results should be included.
   - **Ordering:** specify it when the question requires it.

Before coding, fill in this short planning template:

```text
One output row represents:
Required input records:
Information I need to join:
Calculation:
Grouping or ranking:
Condition for keeping results:
Required ordering:
```

When you get stuck, identify **which line of this plan you cannot complete**. Work on that specific decision. After receiving a hint, write and inspect the next small piece yourself. This is how the approach becomes familiar enough to use independently.
