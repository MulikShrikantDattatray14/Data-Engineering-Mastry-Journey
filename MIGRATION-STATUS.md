# Migration control / preservation checklist

## Existing sources (immutable during migration)

1. [Data-Engineering-Mastry](https://github.com/MulikShrikantDattatray14/Data-Engineering-Mastry) — 552 files / ~29.07 MB at initial tree inventory. Includes SQL Bosscoder, PNP content, original PDF/ZIP/CSV/XLSX assets, Python 80-page source PDF, and 76 Python source-aligned lesson entries. The current repository holds these unchanged at original paths; this branch does not delete them.
2. [data-engineering-journey](https://github.com/MulikShrikantDattatray14/data-engineering-journey) — 192 files / ~0.98 MB at initial tree inventory. Includes study history, dashboard, plans, progress JSON, Bosscoder lecture source-audit notes and reviewed work. The preserved snapshot belongs under `99. Reference Materials/Legacy Journey Snapshot/` once each file is verified.
3. [W3Schools Python](https://www.w3schools.com/python/) and [W3Schools SQL](https://www.w3schools.com/sql/): external official source links only, not scraped/copied lesson pages.
4. ChatGPT Study Mode: verified concepts and original corrections; keep concise novel learning in canonical note, detailed attempts in separate evidence.

## Non-destructive migration rules

- Never delete, overwrite, rename, or force-push the source repositories as part of initial migration.
- Preserve binary materials byte-for-byte, and record old→new paths and SHA/size before declaring migration complete.
- Link to existing source-backed files; never create a second lengthy conceptual explanation simply because another course taught it.
- Do not mark an originally provided Bosscoder/PNP question solved without independent submitted code and verified review.
- Verify every original file has either an untouched resident copy or a verified archived snapshot and a traceable mapping.
- The dashboard should retain real progress only, no invented work on Diwali Nov 7–8.
- Complete source-to-topic coverage auditing for SQL, Python 80-page PDF, seven Bosscoder lecture PDFs, and W3Schools before any “nothing missed” certification.

## Next migration gates

- [x] Both source trees inventoried.
- [x] Staging branch created in existing repository (original main untouched).
- [x] All 192 Journey files snapshotted, with exact path/blob SHA reconciliation (192/192).
- [ ] Every canonical topic linked/mapped to all four sources and unique gaps merged (eight Python canonical foundation chapters and SQL NULL/Joins foundation examples are currently staged).
- [ ] Full functional links, code snippets and visual checks (canonical relative links and sample SQL/Python outputs validated; full interactive dashboard deploy validation pending).
- [ ] Repository created/renamed to `Data-Engineering-Mastry-Journey` (requires capability currently unavailable to this GitHub connection).
- [ ] GitHub Pages moved or configured at new repository location.
- [ ] User-approved final switchover after verification.

## Integrity result

A source-to-snapshot audit verified **552/552 original Mastry** blobs unchanged and **192/192 Journey** blobs identical to their source. The [source inventory](<99. Reference Materials/SOURCE-INVENTORY.json>) records paths and SHA hashes. The migration is not production-ready until the full 4-source topic mapping and final repository cutover are verified.
