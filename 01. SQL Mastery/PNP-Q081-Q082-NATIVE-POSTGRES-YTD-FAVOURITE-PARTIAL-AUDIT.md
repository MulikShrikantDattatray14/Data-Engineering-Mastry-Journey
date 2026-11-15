# PNP Q081/Q082 — original supplier SQL on native PostgreSQL 16 (PARTIAL, 16 November 2026)

## Provenance and exact scope

- Source statement: archived P081, Git blob 054faf9e755d6f7212a7c8906be5165aa922abf8 (source points to PNP PDF pp.153–155); P082, Git blob b12c819076c2418c805dd88a020278c3007a85e0 (PDF pp.156–158).
- Supplied-attributed PostgreSQL answer file: original all_100_solutions.sql, Git blob 7912c8e676621c513e0b635a40c6ee299404676e. Reviewer checks exact bytes and extracts Q81/Q82 SQL unchanged: no SQLite translation or edited query.
- Earlier check_pnp_81_88_source_answers.py has **already** inspected both statements and executed compatibility-adapted SQLite examples. This is **new native-engine evidence, not 2 newly unique keys**; conservative clean supplier-key replay count remains 94/205.
- P081/P082 archived Markdown historical status remains NOT SOLVED YET, learner solutions Pending, official solution display Pending. Provider-authenticated grade or official-key correctness: NOT VERIFIED. Original PDF page images: NOT VERIFIED. Full original Commerce CSV and measured data-quality distribution: NOT VERIFIED. No learner independent solve or mastery is claimed.

## Bounded reviewer test contracts

Source-pinned native PostgreSQL 16 reviewer: scripts/check_pnp_q081_q082_native_postgres_boundaries.py. The 19 unittest methods cover immutable source blobs and engine identity; Q081's supplied leap-day four-row illustration, nonleap same-period boundary, missing prior and zero denominator, NULL amount, missing or empty dated anchor; Q082's supplied Audio 2/3 illustration, units/order-count/recency/alphabetical tie precedence, missing product, zero units, customer identity, missing details and an actual-category-name-versus-Unmapped label collision.

**Conditional source-key discrepancy reproduced in synthetic fixtures:** PostgreSQL DESC order places NULL date first by default. Q082 sorts by last_bought DESC without NULLS LAST. If an order with NULL OrderDate has the same category units and distinct-order count as a genuinely dated order, the key selects the undated category as most recent. The original Commerce v2 loader declares Orders.OrderDate nullable, but the source CSV's actual NULL date count has not been verified. This is NOT proof of a provider grading error or a bad real-data row.

Other explicit boundaries: P081 returns a single NULL-period/zero-orders row when no usable OrderDate exists (policy unspecified); P082 folds a real CategoryName literally "Unmapped" into the missing-category bucket; an all-zero unit denominator results in NULL percentage, not zero. These fixture behaviors are not independently asserted to be incorrect under a provider-specified policy.

## Evidence tiers and limitations

- Indexed: previously YES for both.
- Original source statements individually inspected: YES, rechecked original blob identities.
- Native unmodified supplier SQL on reviewer-only synthetic test data: tests added, **check named test and CI logs before marking PASS**.
- Provider-authenticated answer correctness / native original full-dataset output: NO.
- Independently learner-solved / Academy-graded / mastery: NO.
- Licensing/privacy, PNP PDF rendered-page parity and full 205-question source-to-concept signoff: NOT DONE.
- Preserve source archive and all historical learner attempts; no interactive-study-derived sync before complete independent audit signoff, followed by separate post-sync CI.


## Independent implementation-head CI proof (16 November 2026)

- [GitHub Actions run 43774377505](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43774377505) **completed/success** at exact SHA 2dfec95855d0d46e627d7bf54a1914f766a695d9, independently confirmed matching live main at validation time.
- Independently decoded native PostgreSQL job 132997186260 logs: **all nineteen named SourceQ081Q082NativePostgres tests ... ok; Ran 19 tests; OK**. **153/153 general validation, 23/23 native PostgreSQL and 9/9 native MySQL steps succeeded**, zero failed/skipped. These checks validate synthetic source-key fixtures, not authenticated provider grading or original full-CSV output.
- The additive proof documentation is a later commit than the tested implementation SHA. Its own exact-main CI must be checked separately before final-head PASS can be declared.
