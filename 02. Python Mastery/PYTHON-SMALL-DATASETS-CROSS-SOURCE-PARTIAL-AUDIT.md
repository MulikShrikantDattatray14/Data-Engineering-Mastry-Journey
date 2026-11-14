# Independent partial Python mentorship fixture and linked-lesson audit — 14 November 2026

**Evidence scope:** nine preserved original small training input files and four exact archived PDF-linked **companion Markdown** files read individually; independent original input/relationship calculations; distinct reviewer-created synthetic counterexamples. **Not original 80-page PDF visual/text parity, PNP provider answer-key authentication, graded learner coursework, production ETL or learner mastery.** No original bytes, historical learner progress or canonical teaching notes changed.

## Exact immutable original source identities

These source paths are relative to the preserved 2. Python Mastry archive. The [read-only executable checker](../scripts/check_python_training_fixture_cross_source.py) verifies all **13 original Git blob SHA-1** identities.

| Original source | Git blob SHA | Direct finding |
|---|---|---|
| python_de_dataset/employees.csv | 08d2330cc9dab1530d6ff8e896211f7867438e4b | 9 employees, one root, manager links resolve |
| python_de_dataset/logins.csv | e5669aa40eb3a08569355351eaa1c4f6e35a556d | 12 login records |
| python_de_dataset/order_items.csv | 072bd904c499ce5547049eb8ba0fc2dd4c071cd0 | 24 order-item rows |
| python_de_dataset/orders.csv | 2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2 | 15 order headers |
| python_de_dataset/orders_dirty.csv | e36bedf1e6b9b5ef2582b007440c92ccf9fda83a | 7 deliberately dirty input rows |
| python_de_dataset/products.csv | c5beff443efbdc3cd73376cd721334fa0bf43d8b | 8 product identifiers |
| python_de_dataset/snapshot_day1.csv | 12043a47a749ea54c89ae2becb509e22c991b399 | 8 snapshot keys |
| python_de_dataset/snapshot_day2.csv | 3966cea9b4f16dd9a7ac0da6d4beff201a60c7a1 | 8 snapshot keys |
| python_de_dataset/customers.json | d6125fce237e7f7e3193667946d1eb117cd19db0 | 8 distinct customer keys |
| 2. Python Foundations/09. Files CSV JSON JSON Lines and paths.md | 54e71278f26aa0d2847363e4860cbac98b1caaa7 | Original PDF-linked p.33 |
| 5. Coding Round Patterns/11. Validation and snapshot differences.md | aa3ae4081c26bf16ea221a28c552535be53abefe | Original PDF-linked p.68 |
| 6. Python for Data Engineering/04. Build an idempotent ETL pipeline.md | fc859b44748d06318f2d0bdb4ae36266715253e7 | Original PDF-linked p.72 |
| 6. Python for Data Engineering/05. Testing and data quality.md | 05b4ff35d2666ef5908237686f2a517dd718301a | Original PDF-linked p.73 |

## Direct source-input/output reconciliation

All eight CSV headers and complete row counts inspected, together with the eight customer JSON records. Each of the **15 original order headers** independently reconciles to the **24 original order item rows** using Decimal at the original line-amount grain: **zero order-level differences**, aggregate **23,268.00**. Twelve delivered, two cancelled, one returned; delivered-only gross amount **18,972.00**. Whether either sum represents recognized business revenue **has not been established**. All clean input order/customer, order/item, item/product and employee/manager references resolve inside this small training fixture. No production source, current price history or real warehouse validation is implied.

Seven original dirty input records: order 116 negative amount, 117 missing customer, 118 invalid calendar date, 119 unsupported status, 120 nonnumeric amount, 121 accepted, 122 accepted after status trim/lowercase. This agrees with source p.68 sample normalized output. **Source p.73 raw pandas quality example does not test calendar validity**: its four failed check labels do not imply that it detected February 30. A source date-validation extension appears as a separate **unsolved Your turn**. Snapshot day 1 to day 2 yields added ID **9**, removed ID **8**, city changes for IDs **4** and **6**; source p.68 demonstrates the same illustrative diff. This proves only a snapshot-difference calculation, **not** real change-event ordering, deletes or SCD2 time semantics.

## Distinct reviewer-only counterexamples

In-memory header-level summation after joining original two-line order 101 gives **2,396**, double the actual source line sum **1,198**. Hypothetically changing a current catalogue price generates **1,398** rather than original historical source line pricing **1,198**. A fabricated four-fault dirty row returns four rejection reasons; a fabricated duplicate snapshot customer row shows last-key-wins dictionary loss. All synthetic modifications are ephemeral; none occurred in any original file. The checker verifies each case separately from the preserved original data.

## Evidence tiers and remaining gaps

**Indexed** = preserved file paths and lesson references. **Statement/input inspected** = all nine actual dataset inputs and four linked companion source texts. **Source-data calculated** = all 15 header/item amounts, source cross-file references, dirty data partition and snapshot transitions. **Synthetic test passed** = only after exact-final-SHA CI confirmation. **Official answer verified** = 0 new; no independent original provider PDF grading. **Learner independently solved** = 0 new; no mastery. Conservatively verified PNP SQL supplied-key replay remains **94/205**.

Full original PDF page/prompt fidelity, remaining source examples, all official PNP SQL outputs/full commerce data/native dialects, Bosscoder and W3Schools original materials, other DE domains, licensing/privacy/binary content and comprehensive source-to-concept integrity remain unfinished. Issue #1 **OPEN**. ChatGPT Library pending study record and later interactive practice **UNSYNCED** with GitHub until full audit signoff and separate learning-sync CI.
