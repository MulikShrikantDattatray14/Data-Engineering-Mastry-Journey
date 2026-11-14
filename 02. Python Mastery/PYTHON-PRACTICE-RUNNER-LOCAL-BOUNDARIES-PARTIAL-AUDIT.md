# Original Python mentorship local practice-runner — independent PARTIAL audit, 14 November 2026

**Evidence scope:** eight preserved original tooling, launcher, requirements, teaching and data sources inspected byte-for-byte, and a new read-only [eight-method reviewer checker](../scripts/check_python_practice_runner_original_safety.py). This verifies a different **runner integration path** for previously audited PDF page 23, not additional distinct pages or new completed exercises. Original PDF rendered-page parity, official grading and OS-sandbox safety remain unverified.

## Eight immutable archived source identities

Paths are relative to the original archived 2. Python Mastry directory. Git blob SHA-1 identities are rechecked before importing the runner and after reviewer tests.

| Original path | Git blob SHA-1 | Independently inspected purpose |
|---|---|---|
| practice_runner.py | 46e478f026212896440343d37443ba44fa193248 | Local browser UI, source fence handling, transient scratch execution |
| Start Practice.cmd | 13da483db0d607ec766677f80313d571bbdac889 | Windows launcher: Python 3.14 path, fallback to py |
| requirements-practice.txt | f6d8f15b4129386f70f03cc51d859ca7f440f411 | Optional pandas, numpy, pytest (unpinned) |
| 00. Start Here.md | 6ac4f64ce4e2906a3936d7886c0f2bbed1ace9fa | Original introductory source text, three fenced snippets |
| 1. Python from Zero/01. Your first Python program.md | 5fd194caa2280c436371fb94cee97f1ee4c5f5fb | Archived lesson identity and index selection |
| 1. Python from Zero/19. Mini project - monthly sales report.md | 30992048e800aa0aaf8e8940546993d5b48be366 | Original five-block lesson for end-to-end runner test |
| python_de_dataset/orders.csv | 2d08d1fc6acdc4f26c4427f27ac7925bfb202ea2 | Original 15-row source input, scratch copied |
| python_de_dataset/README.md | 42ba92515379976a0d1cdd42114aa64c9a1daa9e | Original working-directory and record-count guide |

## What the reviewer checker checks

One immutable source-identity method, one parts/lessons inventory method and one fence/named-file parsing method read the untouched original sources. The original page-23 monthly report is run via the original runner with its automatic predecessor-snippet setup, on a temporary copy of the genuine source CSV. The expected supplied-example output includes 15 orders and 18,972.00 delivered-only revenue; this is a **publisher demonstration replay**, not a learner solution or verified provider grade.

Four additional **synthetic reviewer-only** methods check that edited print-only source lives in a disposable workspace rather than modifying the archive, over-size source/stdin rejection, a one-second synthetic process timeout, synthetic stdout truncation, and loopback HTTP Host, Origin, session-token rejection/approval in a temporary local-only server. These are narrow runtime tests, not general security certification. All original archival paths are source-hash guarded.

## Findings and unresolved boundaries

- **High-value security caveat:** Original runner executes user-edited arbitrary Python with the host interpreter, inheriting its environment. A scratch working directory, 8-second child-process timeout, 64-KB output budget, loopback binding, random browser token, Host/Origin checks are **not an OS sandbox** or a guarantee against filesystem/network/process access, memory exhaustion or descendant subprocesses. Use only trusted local code; never publish as a remotely shared untrusted code executor. Do not infer a vulnerability in the local-token guards from their presence.
- **Windows and dependencies not certified:** Original Windows batch launcher is inspected only, not executed on Windows. Optional pandas/numpy/pytest versions are unpinned, so cross-machine reproducibility is unproven.
- **No auto study sync:** Local runner scratch workspace and browser localStorage drafts are not GitHub learner-completion records. No reviewer exercise or publisher example may be credited as independently learner-solved.
- **Not a source-PDF or licensing signoff:** Original 80-page rendered PDF comparison, ZIP/binary privacy parity, paid-content redistribution rights, full external Bosscoder/W3Schools tests, remaining DE subjects and comprehensive source-to-concept reconciliation are unfinished.

**Tier interpretation:** indexed = eight archive files; statement and code inspected = eight files; source demo replay = archived runner page-23 demonstration once CI passes; synthetic tests passed = only after exact-head CI log validation; official answer newly authenticated = **0**; independently learner solved = **0**; mastery = **0**. Conservative PNP supplied-key replay still **94/205**. Keep GitHub Issue #1 OPEN. ChatGPT Library pending learner study record and later practice remain UNSYNCED until independent full-audit signoff and separate successful post-sync CI.
