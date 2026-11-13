# Bosscoder Python Lecture-05 OOP: 12 pending MCQ semantic checks (independent, partial)

Audit date: 2026-11-13. Scope: **all twelve individual saved derived assignment statements** under `99. Reference Materials/Legacy Journey Snapshot/02-python/bosscoder/lecture-05/assignments/`. These public records explicitly describe study-purpose paraphrases of private Academy screenshots. Exact original programs, exact call/print sequences, official answers and grading were **not supplied** here. No learner attempt has been claimed. Previously indexed/source-note-checked does not mean authenticated.

## Immutable individual source inspection

| ID | Saved assessment topic | Original Git blob SHA | Current historical learner state |
|---|---|---|---|
| Q01 | q01-class-instance-attributes | `5af9009d9f01b17366c641efcd54f0b16910c969` | Chosen Pending; Review Pending; platform Not verified |
| Q02 | q02-private-name-hasattr | `f34d83fabdef488eb501ec8dda7eef60d436cd52` | Chosen Pending; Review Pending; platform Not verified |
| Q03 | q03-method-shadowing | `9ba45edd4052c7e436ca54ef12ff8845946a0d4a` | Chosen Pending; Review Pending; platform Not verified |
| Q04 | q04-staticmethod-class-call | `4189716be2e86ec62cb2598fb7648031751b7d5b` | Chosen Pending; Review Pending; platform Not verified |
| Q05 | q05-method-shadowing-variant | `fe2b5837a64ba60d1f2ea696b5a29c62632241a2` | Chosen Pending; Review Pending; platform Not verified |
| Q06 | q06-abstract-class | `74ae715d294ac099291724c7434c9102af0ede68` | Chosen Pending; Review Pending; platform Not verified |
| Q07 | q07-polymorphic-override | `5a18928eb83ee05720444bb77d3645634a968b5d` | Chosen Pending; Review Pending; platform Not verified |
| Q08 | q08-diamond-method-resolution | `d2fc2d897589947e1fb6f4aafecf9101bbb55357` | Chosen Pending; Review Pending; platform Not verified |
| Q09 | q09-mro-tuple | `46d2054921d7a907be8640afb16922db0c18f5de` | Chosen Pending; Review Pending; platform Not verified |
| Q10 | q10-subclass-constructor | `9593fa307e7a692c97672252c4da5cdae70d5926` | Chosen Pending; Review Pending; platform Not verified |
| Q11 | q11-shared-class-list | `ad68c62247b10da80e11d7680ec74867e27b832b` | Chosen Pending; Review Pending; platform Not verified |
| Q12 | q12-explicit-super | `4ef15709785cf6f7a34759682631aaef17ab21a9` | Chosen Pending; Review Pending; platform Not verified |

Each of the 12 original question files was individually read, including its four-choice text, concept, and untouched attempt/review state. The assignment README confirms **0/12 reviewed**. Q03/Q05 are distinct questions with overlapping theory; neither may be deleted or marked solved. Q01–Q08 contain a duplicated "Four choices" section. Q06's two choice sections disagree about the wording of choice 2 ("Error due to unimplemented abstract method" versus "Error: abstract class not implemented"); this is a saved-derivative editorial inconsistency, **not** a proven Academy screenshot error.

## Exactly what was independently tested

Read-only checker: `scripts/check_bosscoder_oop_05_pending_mcq_semantics.py`. Source SHA and Pending guards plus 11 behavior tests (**12 total unittest methods**) cover Q01 class-vs-instance lookup and deletion, Q02 actual name-mangling/hasattr, Q03/Q05 method-shadowing and calling the overwritten string, Q04 static vs regular binding and missing self, Q06 abstract subclass creation, Q07 dynamic dispatch, Q08 C3 diamond MRO and three possible inherited implementations, Q09 ordered multiple bases, Q10 constructor override with and without explicit super, Q11 mutable shared class list and instance rebinding, and Q12 explicit `super(B, instance)`. All behaviors are **auditor-created Python miniatures**, not the absent Academy code or authenticated official output. Pending states remain untouched. CI outcome is recorded separately when validated.

## Independently reproduced acceptance risks and blockers

- **Q04** exact original class/instance invocation sequence is absent. The valid result vs missing-self TypeError cannot be resolved from a paraphrase alone.
- **Q08** class declaration order and which classes override the method are absent: independent variants return A, B or C. No unique answer can be authenticated.
- **Q09** inherits two unspecified bases in the paraphrase; the base order matters for the exact `__mro__` tuple.
- **Q10** source paraphrase does not say whether the child explicitly calls `super().__init__()`; the independently demonstrated output changes.
- **Q06** repeated answer-option wording differs within the saved source; exact original Academy wording cannot be authenticated.
- **All Q01–Q12** original private Academy screenshots/executable snippets, the Academy's marked answer key, actual platform submissions, judges and learner selections are unavailable; **no official answer verified / no learner independently solved / no mastery or duration credit**. Reproducing a plausible Python behavior is only **synthetic reviewer testing**.

Evidence tiers: twelve **indexed**, twelve **statement inspected**, twelve **source-hash pinned and reviewer-synthetic tested** (subject to independently verified CI), zero **authenticated official answers**, zero **learner independently solved** from these records. The base Lecture-05 teaching-note checker already existed; this addition does not authenticate screenshots or other subjects.

**Still open:** all-original PDF parity, remainder of PNP SQL/mentorship/Bosscoder/W3Schools/DE work, source-to-concept, integrity/privacy/licensing and full-audit final signoff. PNP clean bounded original-key replay remains **94/205**, unchanged. Original archives and historical attempts/progress stay read-only. Separate ChatGPT Library pending-study record and later learner practice are **UNSYNCED to GitHub** until independent full-audit signoff, then require separate scoped learning-sync commits and post-sync CI.
