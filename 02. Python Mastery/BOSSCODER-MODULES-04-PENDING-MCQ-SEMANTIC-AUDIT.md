# Bosscoder Lecture-04 exceptions: 11 pending MCQs — partial source-by-source semantic audit

Audit date: 2026-11-13. Evidence tier: each public screenshot-paraphrased question separately inspected + exact archival Git blob SHA; independent reviewer-authored Python runtime demonstrations. **NOT:** primary Academy screenshot authentication, official answer, actual submission, learner choice or mastery.

Immutable original directory: 99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-04/assignments/ (never edit). Reproducible reviewer checker: [source-pinned Python semantics](../scripts/check_bosscoder_modules_04_pending_mcq_semantics.py). The existing [Lecture-04 PDF/notes audit](BOSSCODER-MODULES-04-INDEPENDENT-AUDIT.md) covered selected private PDF examples separately; it did NOT authenticate the Academy MCQ wording or grade these eleven questions.

## Separately inspected archived question statements

| MCQ | Source Git blob SHA | Individually checked reviewer evidence | Unresolved source/acceptance gap |
|---|---|---|---|
| Q01 | 2da86260dc526bc5207de315bebd8d20aad9fe89 | Coroutine exceptions: independent asyncio probes demonstrate exception handling inside coroutine and around await; await alone propagates. | Two alternatives describe valid behavior. Original single- vs multi-select grading missing. |
| Q02 | 5ef441ab29e04249bdb347a6c0317bb2879d26a0 | Synthetic nested try/except/finally trace after handling inner division error. | Exact Academy program absent; no authenticated print order. |
| Q03 | e846847aea325e52df9988c286601e06f27d0501 | Reviewer explicit raise statement and assertRaises verify interpreter semantics. | No official selected option or learner response. |
| Q04 | 2dde93666919e6b35338397f8e292ba5d2df610f | Finally exercised after normal exit, caught exception and return. | Normal language control flow, not guaranteed under abrupt interpreter/process kill. |
| Q05 | 667e329c8db55534e69115940e3a75c0b9e02aa1 | ExitStack dynamic entry of three contexts, reverse cleanup, default propagation and optional suppression. | No provider answer authentication. |
| Q06 | 5dfe9de35078ee849a7818c88175118d4cb88307 | Reviewer explicit exception chaining distinguishes wrapper message from cause type/message. | Exact original class, print expression and expected text not preserved. |
| Q07 | 7b3e407edf04b37e1b929195139567dba09f677b | Reviewer ZeroDivisionError handler appends a custom warning. | Precise archived source print text/code absent. |
| Q08 | abc35b782290ba0de7d0cb00dc51a02851d1e7d0 | Exception propagation through caller checked; uncaught top-level errors also terminate execution. | Two paraphrased answers can be true under different scopes; wording says may happen. |
| Q09 | 8866d908c51ec752cdffe6c1dd4132571dab4364 | Near-duplicate coroutine handling question separately inspected; combined independent Q01/Q09 probes. | Same ambiguity; not an additional learner completion. |
| Q10 | 2c53992126b23446d531b0e520484448efb10fa2 | Reviewer handler with tuple of ValueError and KeyError catches both; TypeError separate. | A shared single handler differs from multiple separate handlers; no official answer authenticated. |
| Q11 | a8ab3c28d5e8ede1cc4118c8c714d2ecb4fccbbc | Two alternate nested-function implementations produce distinct correct catch/finally traces. | Exact original two-function code and catch placement absent; definitive original output unjustified. |

## Evidence-tier and status controls

- Original 11 Markdown source records are exact Git-blob pinned, marked practice paraphrase, and retain **Selection: Pending** and **Reviewed: Pending**. The original assignment README preserves **0/11 reviewed**. Neither learner attempts nor provider keys were changed.
- New Python standard-library unittest reviewer checker defines **11 tests**: immutable guard for all eleven source records, combined Q01/Q09 coroutine cases, and separate synthetic behavior checks for Q02–Q08 plus Q10/Q11. All source programs used in runtime probes are **auditor authored**, not full original Academy question code.
- **Independently observed code+documentation-head CI:** [GitHub Actions run 43388969450](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry-Journey/actions/runs/43388969450), exact source/documentation commit 16ffd4816db3cae8e56691b0d200d4753fbe656c, completed SUCCESS. All 11 source-pinned reviewer methods PASS in decoded validation job 131764055196; validation 99/99 and native PostgreSQL 18/18 steps successful, 0 failed/skipped. Any later evidence-only commit still requires its own exact-head CI check. Green synthetics do NOT authenticate missing Academy original screenshots, answer keys, hidden tests, source print output or student grades.
- The PNP SQL clean bounded supplied-key replay remains **94/205** unique P-series IDs, unchanged. Remaining original SQL PDF/full dataset and contract parity; Python mentorship; Bosscoder/W3Schools/other DE subjects; cross-source completeness, licensing/privacy and comprehensive final signoff remain pending.
- **Issue #1 OPEN; learning sync gated.** ChatGPT Library /Data Engineering Study/DE_LEARNING_PENDING_GITHUB_SYNC_2026-11-09.md and subsequent learner work stay UNSYNCED to GitHub until full independent signoff and a separate successful post-sync CI.
