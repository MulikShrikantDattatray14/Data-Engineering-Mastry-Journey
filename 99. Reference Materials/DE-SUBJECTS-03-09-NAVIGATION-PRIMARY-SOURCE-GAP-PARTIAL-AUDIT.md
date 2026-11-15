# Independent DE subjects 03–09 navigation and source-content gap (15 November 2026)

**PARTIAL audit only.** This is a read-only, exact-Git-blob-pinned structural review, not substantive verification of complete Bosscoder cloud/DE coursework, vendor platform labs, a runnable Spark cluster, course answers, learner mastery, production projects, licensing or privacy.

## Independently reopened sources

The newly added [12-test reviewer](../scripts/check_de_subject_03_09_navigation_primary_gap.py) opens and checks **18** preserved text blobs: seven current subject navigation READMEs, seven corresponding original Legacy Journey READMEs, and four Original Mastery Python-for-Data-Engineering lessons. The reviewer computes the Git blob SHA of the physical bytes rather than relying on a filename or an index. The following are the exact current/source pairs:

| Current subject README SHA | Corresponding original Legacy Journey README SHA | Finding |
|---|---|---|
| 03 Database Design and Modeling `215c6ddf41469f358b94136171ff987cd93a3e3e` | 03-databases-and-modeling `4db710f5f27e287371cc7b4c0305b6ff911e36de` | Topic outline; no subject-specific canonical foundation note or graded model |
| 04 Data Pipelines and ETL `05a997b9d4c09d5ea21a16bdcb213b10fcdc83be` | 04-data-pipelines `218394bcb218acbcc4bb7689077e73b5f8e8c270` | Outline; a separate original Python ETL example exists in the immutable archive |
| 05 Apache Spark `ba8cd95c358edc8944a701cccca115c471a8a3eb` | 05-apache-spark `5a26de48654861b7d4c9fef15e622a6e18bde59f` | Outline; source Python chapter explicitly requires an external Spark runtime |
| 06 Cloud and Orchestration `11f33ad7d1a3b375b635fb7690d7e733862654a2` | 06-cloud-and-orchestration `5a0fa8f0f4932f40d2f465c13403969068568479` | Outline; original Airflow example has unimplemented warehouse integration |
| 07 Data System Design `f3cf7358f2e0f94c5fa1b963abcc0621894a9c32` | 07-system-design `b448fe0bfcd999d407c9d883629f86395030d2d0` | Design priorities only; no reviewed architecture project in this subject folder |
| 08 Projects `e53094174369888c49abbb80257ec1ea16612a61` | 08-projects `decd51027e1e60142ff661eca76868aaf8315aef` | Original explicitly calls two projects **candidates — not yet built** |
| 09 Interview Preparation `c02fb34faf5c712cdd58591e4075aa4f7cbb8b87` | 09-interview-preparation `fa722660dea3999723d34df9e54d56781e97d812` | Planning/rubric outline, not verified mock-interview outcome |

All **seven current subject folders presently contain a README alone**, and all seven README bodies explicitly disclaim completed curriculum. Each links to the Legacy Journey snapshot *root*, not to a subject-specific verified lesson or assignment. These are **explicit navigation and subject-specific material gaps**, not proof that the entire archived repository lacks the relevant concepts. The four related lessons examined below are physically preserved elsewhere. The reviewer intentionally does not assign learner mastery, automatically fill foundation notes, or mutate history.

## Four original examples independently inspected, not double-counted

| Preserved Original Mastery chapter | Exact Git blob SHA | Bounded observation |
|---|---|---|
| Python DE 03 — Python and databases, source-attributed PDF p.71 | `02af93e471c9f933274981230981102c72e76d69` | SQLite parameters, intentionally unsafe comparison, transactions; not a certified cloud database lab |
| Python DE 04 — Build an idempotent ETL pipeline, p.72 | `fc859b44748d06318f2d0bdb4ae36266715253e7` | Extract/transform/date-partition DELETE+INSERT within a SQLite transaction; not linked from subject 04's README |
| Python DE 05 — Testing and data quality, p.73 | `05b4ff35d2666ef5908237686f2a517dd718301a` | Validation functions are a separate example and **not wired** into p.72's load |
| Python DE 06 — From pandas to PySpark and Airflow, p.74 | `17b999bcc639f184c5ca7bac4c3a325d4d05e763` | Source explicitly says optional external packages and nonexecuted Airflow model; DAG has `NotImplementedError` warehouse placeholder |

These four were **already inspected or tested elsewhere** (see [mentorship ETL p71–74 prior ledger](../02.%20Python%20Mastery/PYTHON-ETL-P71-P74-SOURCE-CONTRACTS-PARTIAL-AUDIT.md)). They are re-opened here to check **cross-subject discoverability and curriculum-integrity boundaries**, with **zero new unique lessons, official answers or learner completions** claimed.

## New checks and evidence tiers

Twelve tests guard: all 18 Git blob SHA identities, seven current folder membership sets, honest navigation disclaimers, valid Legacy-root links, original outline scope, unbuilt project wording, cross-subject archived ETL/validation contracts, PySpark/Airflow not-executed caveats, parameterized database example and absent subject-specific canonical foundations. These are **structural and original-statement-inspected** checks; no new execution of original supplier application, Bosscoder paid module, AWS/GCP resource or official answer key is asserted. Test PASS requires **independent GitHub Actions job and exact-HEAD verification**; the script's presence alone does not establish it.

## Still blocked / outstanding for Issue #1

- Inspect original private Bosscoder Cloud and Data Engineering Tools recordings/slides/assignments and any official grading, and source-to-concept compare all required topics, diagrams and projects. **None were authenticated by this run.**
- Source-specific full lesson material and independently reviewed deliverables for current subject sections 03–09 remain unestablished; do **not** interpret a placeholder README or archived topic outline as completed course material.
- Original source PDFs and binary page rendering, full PNP SQL 205-question meaning/answer/output parity, complete Python/W3Schools/Bosscoder/other DE review, source redistributability/PII and comprehensive signoff remain pending.
- Evidence tiers unchanged: indexed / structural source text inspected / bounded checker (if CI PASS) are **not** authenticated official answers, independently solved coursework or mastery. Previous conservative clean PNP supplied-key tally **94/205 unchanged**.
- Original archives, historical learner attempts/progress, canonical Python/SQL foundations and progress files remain outside this change. The separate ChatGPT Library learning record and subsequent interactive study must remain **UNSYNCED to GitHub** until full audit signoff, scoped post-audit sync, and separately verified post-sync CI.

**Keep Issue #1 OPEN and do not notify the user of completion.**
