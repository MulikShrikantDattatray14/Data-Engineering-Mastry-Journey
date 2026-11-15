# PNP Advanced A085–A090 native MySQL 8.0 partial source-and-dialect audit

**15 November 2026 — independent audit only.** Six archived original Markdown questions were reopened from the immutable Original Mastery Snapshot (PDF attribution: Advanced SQL 100 Query Questions Vol. 1 p.17). Their source Git blobs were independently checked again, and all historical NOT SOLVED YET, SQLite Pending, SQL Server Pending, and Official solution Pending fields remain unchanged. These six were previously indexed and statement-inspected; this pass adds **zero newly unique inspected question IDs**.

## Exact original source Git blob SHA-1 pins

| ID | Original source SHA | Distinction verified in archived Markdown |
|---|---|---|
| A085 | 3d7d0259231887892bd70f70cd017333ccda7001 | Group duplicate `(order_id,paid_at)`; local illustration 2 matching rows |
| A086 | bb228c4f897bd6b93d25de198cd3f9bd3fc033eb | Local illustration keeps earliest payment **per order_id**, not per duplicate pair |
| A087 | d701707e2810e2d9065f2bb362e35f8310a5d8ba | DELETE duplicates, retain minimum payment_id; local illustration uses pair key |
| A088 | 4426613948ef36cf4d5d7bf67e5e4eca3cc0ea4e | **The unchanged archived DELETE SQL itself** directly selects MIN(payment_id) from its own target payments table |
| A089 | b93db48be869c37c1b28b47b70d755ca87bd4666 | Local illustration: 2 duplicate groups and 3 excess rows |
| A090 | c8f9f650232f532b202677d8cfd75f0eda4d041f | Local illustration uses customer_snapshots extra relation and `updated_at` then `version` |

## Native audit method (no supplier answer or learner submission)

New read-only source-pinned test code: [native MySQL 8 reviewer](../scripts/check_pnp_advanced_85_90_native_mysql.py). Added a separate disposable `mysql:8.0` GitHub Actions service job. It connects only to the temporary `audit` database and drops/recreates its reviewer tables. The original source archives and canonical notes are never written. The tests explicitly require `SELECT VERSION()` to be 8.0.x; any other server version fails instead of silently qualifying.

Thirteen independent unittest methods include immutable source/learner-status guard, native execution of the **actual unchanged A088 SQL** and check for MySQL Error 1093 with zero deletion, reviewer-authored self-JOIN repair, archived local illustrative A085/A086/A089/A090 cases, native NULL-safe `<=>` versus ordinary equals, idempotent minimum-ID DELETE, rollback restoration, unresolved timestamp policy and exact same-timestamp/version snapshot ties, and **243 enumerated five-row payment-key assignments** cross-checked with independently authored Python Counter oracle. Reproduced archived local examples are not asserted to be original supplier PDF output.

**Important dialect separation:** previous source-pinned SQLite reviewer ran original A088 SQL successfully in SQLite; this job specifically probes native MySQL behavior. Even a green native MySQL reviewer proves only those controlled fixtures and dialect error behavior—not the supplier's official MySQL solution or grader, underlying original dataset, PDF visual parity, production delete safety, or a learner independently solving coursework.

**Unresolved policy questions:** A086 earliest payment per order versus A085/A087/A089 duplicate pair key; NULL paid_at default ordering; whether NULL order IDs are valid; A090 missing original extra table schema and full-row unique tie-break; deletion FK/transaction/isolation/permissions and MySQL 8.0 version patch; official answer and original PDF page 17 inspection. Reviewer self-JOIN is expressly an auditor-authored hypothetical repair, not a source or learner answer.

**State taxonomy:** indexed **yes (previous)**; statement inspected **yes (previous, reread here)**; native synthetic test **pending completed matching-head CI and decoded named logs**; official answer verified **no**; independently learner-solved **no**. PNP conservative supplied-key authentication stays **94/205**; six checks add **0** to it.

**Preservation/gating:** Only new reviewer, audit evidence, workflow and additive status changed. All original archive bytes, historical learner attempts/progress, and canonical foundation notes remain untouched; no study-session-derived sync. GitHub Issue #1 must stay OPEN. ChatGPT Library pending record remains UNSYNCED until full independent audit signoff and a separate post-sync CI.
