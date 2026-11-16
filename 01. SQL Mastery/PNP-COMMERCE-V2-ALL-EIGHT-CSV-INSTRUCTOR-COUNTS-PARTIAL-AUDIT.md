# PrepNPlaced Commerce v2 — full eight-CSV instructor-issue cross-audit (PARTIAL)

**Date:** 16 November 2026. **Source tier:** eight complete *unaltered* original CSVs, original README, original PostgreSQL loader, and original instructor planted-issues key. This extends prior full-catalogue X001–X005 checks and Q083 Category-only checks rather than double-counting their question/answer coverage. [Read-only source-pinned reviewer](../scripts/check_pnp_v2_full_commerce_planted_issues.py).

## Audit scope and boundaries

The reviewer reads all eight original preserved CSV files, validates their exact Git blob identities and full row counts, verifies unique primary IDs under the published loader contract, and calculates actual source-row anomaly counts without reading from synthetic PostgreSQL tables. It independently examines catalog/category references and price, rating and brand hygiene; supplier normalization and emails; payment allowlist spellings and dated Pay Later usage; shippers' usage/orphan references; customer email/never-ordered groups; order header missing keys, amounts, date contradictions and cancellations proxy; order-line orphan references, quantities and duplicate line keys. The instructor key is **an attributed source claim to test**, not a proof of correctness; any mismatch requires investigation, not quiet acceptance. No PII/person-level records are copied into this ledger or printed by the reviewer. The full original data already reside in the preserved public archive and are **not** recopied here.

### Pinned original inputs

| Source | Expected data rows | Git blob SHA |
|---|---:|---|
| Suppliers.csv | 18 | `6a1eb9e7b570d301714bb049a928261afcabcc20` |
| Products.csv | 22,088 | `61c11d7f65434aa38a90ef581acb1256515c3d7d` |
| Category.csv | 12 | `b355b85ddce21146a792aa1bde71b153d1b7d42b` |
| Shippers.csv | 10 | `6c2a327c240c5454e9ed7f22d142529238563493` |
| Payments.csv | 10 | `5986647cdc1fc087d84774de1bca875235d19f1c` |
| Customers.csv | 5,072 | `bbb2995f0758fe5012197b8c71d897c1aca5c65f` |
| Orders.csv | 46,438 | `307acc9ad2f85a79d7637a7958ffd62f2a8fa594` |
| OrderDetails.csv | 168,567 | `ddd2fc4d61ca4cc17a49e3dd19440716f07416ae` |
| README.md | n/a | `eb75fac446057899effefcb10029ff2048674ea2` |
| data/load_dataset_v2.sql | n/a | `3787743252d29268c67c491d6a2eb47c1757c35b` |
| instructor/planted_issues.md | n/a | `6f4da61474880372a6e269b17ffc7958350541e6` |

The two original PDFs are **not** visually rendered or checked for word-for-word coverage here. This is a pure-Python independent source-to-instructor aggregate consistency check, not native PostgreSQL full-load replay, not 100 official answer-output checks, and not evidence of any independently solved learner assignment. Source provenance: original README says consumer orders are generated, catalog products derive from a real retailer, and deliberate data-quality anomalies are included. **Rights/PII audit and redistribution authorization remain unresolved** despite source hash preservation.

## Test evidence and known interpretation risks

The initial commit adds 12 offline unittest methods to the existing general GitHub Actions validation job; exact main-SHA run/log verification is required **after** this commit before claiming any PASS. Source counts to revalidate include the original instructor's product price/catalogue hygiene (12 below-sale markets, six zero market prices, four missing sales prices, ten blank brands, eight trailing product names, 4,360 missing ratings); missing category 5012 (40 products) and unused category 5013; one duplicate supplier normalized name and one missing and one malformed supplier email; seven Yes/two No/one N payment flags and twelve Pay Later post-deactivation orders; two unused shippers and three ID-11 orphans; three space-containing customer emails and 647 never-ordered accounts; orders' 20 missing payment IDs, 25 missing shipper IDs, eight unknown customers, five missing and four zero totals, ten headers lacking lines, 12/9/6 delivery-date contradictions and 320 14-day unshipped orders; order-line 12/15/5 unknown references, ten missing and five zero quantities, and 60 duplicate-field extra rows. These numbers are **source assertions awaiting independent CI replay**, not yet verified execution results in this first commit.

The instructor's **72 duplicate accounts** and other grouped duplicate/submission conventions require explicit group-vs-extra-row reconciliation; reviewer prints safe aggregate normalized-email group and extra-account counts but does not prematurely equate either with official grading semantics. The original order/product/line foreign-key orphans are deliberate; they must not be treated as an unforeseen schema failure. String values remain raw (e.g. Allowed='N', Supplier Country='india ') to avoid manufacturing a cleaned version of the source. Comparisons calculate dates with DD-MM-YYYY, respecting the loader; full native loader/CSV/query parity remains pending.

## Audit status and required next work

**PARTIAL, NOT signed off.** After first CI completion, inspect each named test and correct any assertion mismatch by documenting original-source calculation and why, **never altering original archives to force a pass**. Confirm exact main head, file scope preservation and Issue #1 status. Full Commerce PostgreSQL import, supplier answer keys and rendered PDFs, all 205 question/source-contract signoff, remaining Python/Bosscoder/W3Schools/DE coursework, public distribution rights, personal-data review and source-to-concept reconciliation remain open. Conservative distinct supplied-key replay tally remains **94/205**, unchanged; no authenticated provider answer, independent learner completion, or mastery is gained. Pending ChatGPT Library study record and later learner evidence remain **UNSYNCED** pending final audit signoff and post-sync CI.

## New whole-CSV discrepancy evidence from first exact-head CI (16 November)

The initial [implementation run 43787160283](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43787160283) exposed **two genuine literal-predicate versus instructor-count discrepancies** plus a reviewer implementation bug. **Do not suppress or reinterpret either discrepancy as official-provider grading proof**:

1. **Products Market_Price < Sale_Price: 18 actual full-CSV rows**, despite instructor claiming 12 under that literal predicate. The source also flags **six Market_Price=0 rows**. Excluding zero-market-price rows yields **12 nonzero below-sale rows**; thus 12+6 are disjoint only under an additional Market_Price > 0 condition absent from its documented query. Corrected reviewer asserts 18 literal and 12 nonzero counts against untouched CSV.
2. **Customers Email LIKE '% %': 38 full-CSV rows** contain a literal space; only **three contain an internal space after trimming outer whitespace**. The key calls internal-space issue '3' but recommends raw LIKE, which includes 35 externally padded emails. Corrected reviewer asserts 38 raw and three internal-space results without publishing any address.
3. Original audit helper used sum on expressions sometimes returning None rather than False when date blank; an **auditor-reviewer bug**, not dataset problem. Corrected optional-date counters to explicit bool and kept DD-MM-YYYY source parsing. Date results require new exact-head CI.

The first run reported **nine passed, two failed, one error out of twelve**; changing reviewer interpretations does **not** repair any original archive. Corrected-head CI verification and Issue #1 reporting remain required.
