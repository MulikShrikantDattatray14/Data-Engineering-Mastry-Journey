# Independent mentorship source/output audit — PDF-linked companion pages 75–80 (10 November 2026)

**Scope / evidence boundary.** Six ORIGINAL archived Markdown companions were read individually, including the actual questions, stored examples, displayed output, prose constraints, run/edit links and **22 “Your turn” prompts**. The pages are indexed as Python mentorship PDF pp.75–80, but this is **not yet independent visual/text-by-text comparison with the original 80-page PDF**, external platform grading, official learner answer certification or evidence that the user solved these problems. The source archive and historical attempts remain read-only. Existing [canonical interview/revision guide](<15. Python Interview Practice and Revision/0. Foundation Notes.md>) is the teaching home; this file is an audit ledger, **not a duplicate lesson**.

## Exact immutable companion evidence (original Git blob SHA-1)

| Page | Original file under `99. Reference Materials/Original Mastery Snapshot/2. Python Mastry/7. Practice Prep Flow and Revision/` | Git blob SHA-1 | Original linked runnable blocks | Source practice prompts | Specific contents checked |
| --- | --- | --- | ---: | ---: | --- |
| 75 | `01. Interview set - Python coding.md` | `0fe6a53bdcc34d3e7a8d082759bf67319858a85e` | **4** | **4** | Q39 latest device; Q40 consecutive order-date gap; Q41 Decimal two-sum pairs; Q42 dotted-key unflatten |
| 76 | `02. Interview set - pandas.md` | `4f874710d8e30834aa1d8f78fd4016018c7613b8` | **5** | **5** | Q43 monthly top customer; Q44 MoM percentage; Q45 calendar rolling revenue; Q46 all orders delivered; Q47 first/second wait |
| 77 | `03. Concept questions.md` | `51a81d3ee396a05c426dd2f8c8e2f65ef9a1ae6f` | **1** | **3** | **34 source oral concept question rows** (17 values/functions + 13 data/pipeline + 4 algorithm/complexity), one shallow/deep-copy and Decimal program |
| 78 | `04. Complexity cheat sheet.md` | `d9b4c7c13d4f4b816abeb2579415795d650ea7be` | **2** | **3** | dictionary count/sort and list-vs-set membership program outputs; complexity tables and caveats |
| 79 | `05. Ten-week preparation flow.md` | `cc6862cb0cd01e76ad8fee96fdf52793e3b13a9d` | **0** | **4** | all ten curriculum weeks, sample two-hour day, five-step per-problem routine, **illustrative** practice tracker entries |
| 80 | `06. Final revision sheet.md` | `4d6089583b78516ac36d1ec8d8f1667b35f82cee` | **3** | **3** | count/group/latest, top-k/deque/streak/intervals, batching/retry cap, nine failure traps and last-48-hours checklist |

**Counts from actual archived texts:** 4+5+1+2+0+3 = **15 original Python code/printed-output pairs**, with an EXACT text transcript in a `text` fence after each original Python code fence; 4+5+3+3+4+3 = **22 source ungraded practice prompts**; **nine source-published worked interview Q39–Q47** (not the user's submissions). The p.79 template's “Clean/Slow/Failed” sample entries are examples, **not historical learner accomplishments**.

**Original archived input Git blob hashes:** `python_de_dataset/orders.csv` = `2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2`; `python_de_dataset/events.jsonl` = `975c007a68c336007023a9ebd92ba82f02a6b7c3`. Both hashes are independently pinned in the new CI script, in addition to all six lesson hashes.

## Executable verification and its limits

[Original-source-reading checker](../scripts/check_mentorship_python_pages_75_80.py) reads **the immutable original Markdown on the CI worker**, re-parses all original run/edit IDs and Python/text fences, compiles the code, executes the 15 original scripts **unmodified** in disposable directories against copies of the archived dataset, and requires a clean exit and literal full displayed stdout match. The final pandas examples use the previously CI-pinned `pandas==2.3.3` / `numpy>=2.0,<3` environment. SHA guards run before and after each test; archived files never need mutation.

The runner also checks that the **source actually contains all 22 separately numbered ungraded prompts** and exactly **34 oral question rows**. This is inspection of preserved prompts, NOT any learner answer verification or completion.

Four additional **auditor-authored synthetic boundary checks** (separately from 15 source-published output tests):
1. **p.75 Q39:** equal timestamps keep whichever event arrived first, even if a later same-time event name is lexicographically greater. The source explicitly leaves its desired tie-break as “Your turn.” Missing `props.device` and mixed timezone formats have no handled contract.
2. **p.75 Q41:** two equal-value complementary orders both pair with a prior order, without self-pairing; identical amounts are valid *different order IDs*, and Decimal is parsed from text.
3. **p.75 Q42:** a scalar `address` before `address.city` throws `AttributeError` on the original function, while reversing insertion order silently overwrites an already built nested dictionary. Literal dots in source keys need a defined escape policy.
4. **p.76 Q44:** a source-compatible month of 0.00 followed by a positive revenue month prints infinite growth (`inf%`). The original prose itself acknowledges this zero-denominator policy must be set by business rules.

**Other source-specific contracts discovered by individual review:** p.75 Q40 omits single-order customers and sorts observed dates (duplicate same-day orders yield a zero gap); Q41's result is an enumeration of distinct ID pairs, not unique amount values, so output size can dominate runtime. p.76 Q43 chooses a **single** customer on a tie via `idxmax`; Q45 computes calendar days only for the requested fixed 1–7 April range, including zeros; Q46 excludes customers with no order history rather than assuming vacuous truth; Q47 treats same-day order IDs as a deterministic but domain-defined tie. p.77 GIL, Pandas, Spark, and dataclass nuances depend on runtime/version and are conceptual short answers, not implementation checks. p.78 time complexity claims rely on stated average-case and output-size assumptions. p.79 is a *suggested curriculum* and sample tracker, not mandatory completed learning; p.80's retry code **calculates delay caps but does not sleep, retry requests, or prove a resilient pipeline**.

**Evidence tiers must remain separate:** indexed = 76 lesson references; source statements/examples inspected = six new companions; exact original source-output checks = 15 new checks **only after successful matching CI**; synthetic edge checks = four additional methods; official dataset/answer/platform verification = still unproven; learner independently solved/mastered = **not inferred**. Previously confirmed **303 mixed-tier original output contracts through p.74** would become **318 through p.80** only after green CI for these 15 checks. Do not call the mixed cumulative number byte-for-byte exact transcripts.

## Remaining audit blockers (not silently “done”)

- The **80-page PDF** original visual/text/prompt fidelity has NOT been checked against these Markdown companions; metadata links alone do not establish parity.
- Nine source worked interview answers are not independently solved learner assignments. The 22 variations and 34 oral prompts have no individual verified learner solutions.
- Real Spark/JVM, Airflow, source platform grading, and later-version pandas behavior are not validated by this runner.
- Complete original-dataset + official-key/dialect correctness of the **205 PNP SQL source statements**, Bosscoder Python/SQL class notes and assignments, complete W3Schools source-by-source comparisons, other DE domains, rights/license/privacy checks, exhaustive source-to-concept/diagrams/links, and **final full-audit CI signoff** remain OPEN.
- GitHub Issue #1 remains open. **Do not sync interactive learner work from ChatGPT Library** pending independent full-audit signoff and final passing CI.
