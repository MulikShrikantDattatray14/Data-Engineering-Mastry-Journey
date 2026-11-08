# Per-problem study record contract

Applies to **SQL and Python** in **both repositories**. The original PNP/Bosscoder source files are never overwritten by review notes; create separate question records, and link equivalent records between repositories.

## Problem-first (before learner attempts)

Every question must show:
1. **Question ID, source, date, slot, topic, difficulty, and source link.** Distinguish tutor-authored vs PNP/Bosscoder.
2. **Complete problem statement** *when independently authored or permitted for public reproduction*. For third-party paid material, link source and provide an independently worded summary, preserving constraints without republishing proprietary text.
3. **Input schema / sample data / function signature**, including types, nullable columns, boundary conditions, and relevant assumptions.
4. **Expected sample output**, with matching row/column order where required, or function result/exception for Python.
5. **Detailed explanation of why that output follows** from the requirements and sample data — reasoning about the example without showing a full answer algorithm, SQL reference, Python solution, or graded answer key.
6. **Practice status = pending**, with no learner attempt or completion credited before submission.

The user may explain reasoning first, then build small **independent** steps. Archive each step's exact reasoning, submitted code, **actual executed** output/error (when runnable), and review. Never invent execution. For Python capture stdout, return value, errors, and failing tests. For SQL capture actual SQLite rows, column names, duplicates and ordering; use the same reproducible fixture.

## After the learner attempts and the question is reviewed

Keep these sections distinct and attributable:
1. **Original learner submission — verbatim**, never replace it with corrected code.
2. **Observed output vs expected output**, including detailed differences and the exact test fixture/environment; for Python also capture stdout/return/exception/tests.
3. **Review and independent retries** with every learner-authored revision preserved in order.
4. **Reference solution** written and explained by the assistant *after* the learner's attempt; for a third-party question, mark **official provider solution** only if its authentic answer key was supplied and public storage is authorized.
5. **Progressive walkthrough:** why the technique is appropriate; one consistent example; incremental SQL statements or Python code transformations; **actual intermediate outputs after each stage**, explanations, edge cases, complexity/performance, and Data Engineering relevance. If a stage was not executed, label it illustrative.
6. **SQL:** separate (a) learner-authored SQLite query; (b) assistant-reviewed SQLite reference; (c) assistant-converted **SQL Server (T-SQL)** reference. Preserve valid dialect differences. Never credit SQL Server code to the student or claim SQL Server execution without a runtime.
7. **Python:** learner's original Python solution, corrected learner version, assistant-reviewed Python reference, tests, complexity and explanation. **No invented SQL Server version of Python code.**
8. **Optional new learning (Yes/No)** and exact learner wording if Yes, with stable rule reference and date/question link. No is valid.
9. **Evidence and status:** attempted, reviewed, independently corrected, or mastery-verified (separate). Tutor practice and PNP source completions never double count.
10. **Question-closing remote GitHub commit** after the full review, before advancing to the next question. If not solved independently, record “reviewed / retry pending,” not mastered.

### Confidentiality and ownership

Don't publish proprietary paid-course answer keys, extensive third-party questions, employer secrets or private information in public repositories without authorization. Link to the relevant source and preserve the student's own reasoning and code. A tutor-generated reference is **not** an official academy key. The repository-specific study records cross-link each other; retain the original source curriculum files unchanged.

### Repositories

- [Learning, progress, deep walkthroughs](https://github.com/MulikShrikantDattatray14/data-engineering-journey)
- [PNP SQL/Python source and linked independent study records](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry)
