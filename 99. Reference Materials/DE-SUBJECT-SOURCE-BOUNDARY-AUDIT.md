# Independent legacy Data Engineering source-boundary and publication-risk audit

**Audit date:** 11 November 2026. **Status:** scoped original-source inspection and inventory verified, **NOT completed teaching/content/runtime/licensing signoff**. This file is an audit record, not canonical lessons, an exercise solution, or an interactive learner study sync.

## Exact evidence examined

The original `Legacy Journey Snapshot` contains seven non-SQL/non-Python subject directories, and the repository tree showed **exactly one original README.md in each**. I independently retrieved the exact text of each of those seven preserved READMEs, their Git blob SHA-1s, and each of the seven corresponding canonical navigation README files. Those **14 files** are separately inspected; the eight domain/source examples below are *requirements*, not runnable implementations.

| Preserved source (only file in archived domain) | Original blob SHA-1 | Concrete subjects named by source | Canonical subject currently | Source evidence tier and missing verification |
|---|---|---|---|---|
| `03-databases-and-modeling/README.md` | `4db710f5f27e287371cc7b4c0305b6ff911e36de` | OLTP/OLAP; ER, keys, normalization; facts/dimensions; star schemas; SCDs and trade-offs | `03. Database Design and Modeling/README.md` | Source roadmap **statement inspected**; no schema exercise, DDL, warehouse runtime or diagrams in this archived domain |
| `04-data-pipelines/README.md` | `218394bcb218acbcc4bb7689077e73b5f8e8c270` | ETL/ELT, CDC, increments, idempotency, retries, data contracts and monitoring | `04. Data Pipelines and ETL/README.md` | Roadmap **inspected**; no original pipeline implementation, retry tests, CDC event trace or quality output here |
| `05-apache-spark/README.md` | `5a26de48654861b7d4c9fef15e622a6e18bde59f` | DataFrames, partitions, shuffles, skew, joins, caching, execution plans | `05. Apache Spark/README.md` | Roadmap **inspected**; no Spark code, `explain()`, shuffle metrics or measured optimization results here |
| `06-cloud-and-orchestration/README.md` | `5a0fa8f0f4932f40d2f465c13403969068568479` | IAM, object storage, warehouse, scheduling, Airflow, observability, cost | `06. Cloud and Orchestration/README.md` | Roadmap **inspected**; no deployed account, DAG, cost measurements or IAM policy execution here |
| `07-system-design/README.md` | `b448fe0bfcd999d407c9d883629f86395030d2d0` | Throughput, ordering, consistency, replay, duplication, scale/cost | `07. Data System Design/README.md` | Design criteria **inspected**; no completed architecture, capacity calculation or evaluated trade-off scenario here |
| `08-projects/README.md` | `decd51027e1e60142ff661eca76868aaf8315aef` | Two **candidate**, explicitly **not-yet-built** projects: incremental batch warehouse and event-stream/late-data analytics | `08. Projects/README.md` | Candidate statements **inspected**; **zero projects built, deployed, tested or completed** demonstrated here |
| `09-interview-preparation/README.md` | `fa722660dea3999723d34df9e54d56781e97d812` | Interview prompts, timed attempts, rubrics, debugging and mock feedback | `09. Interview Preparation/README.md` | Tracking policy **inspected**; zero real/mock interview results or provider scores substantiated here |

The seven current canonical `README.md` files each explicitly say they are a *navigation entry, not a claim that the curriculum has been completed*. They **do not have an accompanying canonical `0. Foundation Notes.md` in these seven directories** at this inspection. The legacy source archives have no other content within those domain directories. **Do not infer** that a Bosscoder syllabus mention, a PNP Python snippet mentioning Spark/Airflow, or a course subscription provides unexamined execution evidence. Other repo locations may contain small Python/SQL examples or datasets; the present negative evidence concerns **these seven archived directories only**, not an assertion that no Data Engineering example exists anywhere in the entire repo.

**Evidence-tier reconciliation:** seven indexed legacy domain entries, **7/7 original roadmap statements inspected** and **7/7 canonical navigation notes inspected**; **0 archived domain-specific executable programs or original domain exercise outputs** located inside these seven legacy directories; **0 native Spark/cloud/Airflow runtime checks**, **0 official answers/grades**, **0 independent learner completions or mastery** in this tranche. A source-hash-pinned, read-only [checker](../scripts/check_de_subject_boundaries.py) guards the seven archived files plus scoped non-mastery labels. This is preservation/status testing, **not synthetic course exercise testing**.

## Remaining domain proof requirements

1. **Modeling:** obtain authorized detailed source lesson(s), map ER and normal-form cases, independently execute representative constraints/migration/warehouse SQL, and test SCD Type 1 vs Type 2 historical queries.
2. **ETL/pipelines:** source-aligned idempotent initial/incremental loads, backfill/replay, late inputs, dedup and failure/retry tests with actual output fixtures.
3. **Spark:** authorized source examples and a real PySpark/Spark execution plan with nontrivial partition/skew/shuffle checks; distinguish syntax/dry-run from real jobs.
4. **Cloud/orchestration:** authorized provider-specific source/permissions, runtime DAG or equivalent, re-run and failure evidence, observability, and spend/security boundaries; no fictional deployments.
5. **System design:** original worked scenarios, assumptions, measured or derived capacity/latency, consistent event ordering/replay decisions, trade-off review.
6. **Projects:** actual repository code, reproducible setup, data-quality tests, failure recovery, docs/diagrams, and verified outputs; both legacy proposals stay unbuilt.
7. **Interviews:** actual dated independently completed attempts and evaluation records, kept separate from curated example solutions.

## Public archive licensing / privacy boundary (not legal signoff)

The repository is **public**. An independent recursive Git tree inspection identified **23 archived binary/dataset paths** in the Original Mastery Snapshot with extensions `.pdf` (**4**), `.zip` (**2**), `.xlsx` (**1**) and `.csv` (**16**), including PNP question books, a Python mentorship PDF, and larger SQL training datasets. This is **file-path/size inventory only**; it does **not** establish who owns/authorized redistribution of those bytes, a dataset's provenance, or whether CSV records contain personal information. The repository **has no root `LICENSE` file** at inspection. The archived `Legacy Journey Snapshot/LICENSE` contains an MIT grant for the original Journey author's software/documentation, **not evidence of a third-party training provider's redistribution license**. Consequently no publication/redistribution or privacy clearance is asserted.

**Blocking evidence required:** verify creator/provider-specific copyright/license and redistribution authorization for each protected archive PDF/ZIP/dataset and any privately supplied Bosscoder materials; review potentially sensitive CSV data independently under appropriate access; determine lawful publication settings/remediation with the repository owner. **Preserve** originals and hash records; **do not** silently remove or republish anything on this audit pass. The current public exposure is a potential risk to resolve, not a proven infringement finding.

## Scoped preservation and CI

Added `scripts/check_de_subject_boundaries.py` and its standalone CI step. The checker pins all seven legacy SHA-1 blobs and protects the seven current canonical non-completion labels. Its passing only verifies **source immutability and accurate status representation**. The repository's preexisting 744-source integrity and other SQL/Python tests remain separate gates.

**Outstanding overall audit:** complete all 205 PNP original provider-key/dataset/dialect outcomes where evidence is available, notebook/Academy grade parity, Python mentorship original PDF rendered-page/graded outputs, other external W3Schools comparisons, every untested example/figure, real DE subject work, source-to-concept mapping, privacy/licensing clearance and exact-final-head whole-audit CI. **Issue #1 stays OPEN.** Separate interactive learner records in ChatGPT Library are **not imported to GitHub** before full-audit signoff and final CI.
