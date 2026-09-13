# Feature 232 - plan

**Spec**: [`spec.md`](spec.md), ACCEPTED (`spec-fidelity` FAITHFUL at round 3).

## Constitution check

| principle | how this feature meets it |
|---|---|
| XII (research before a ruling; read what you cite; quote what you cite; judge the source) | the whole feature. FR-002 fixes the order: `source-reader` reads, the SESSION writes the entry from the returned quotes, `source-applicability` judges the source before its numbers land, `quote-check` confirms the passage, `record-format` confirms it reads for a reader |
| XII (a guess is the last resort) | a note that stays absent has its search recorded, so the guess label stays earned rather than assumed |
| XIV (fix defects where you find them) | a source that CONTRADICTS the record is a defect found; FR-004 corrects the record and states the divergence |
| XVI (build what was asked; a spec is reviewed by someone else) | three rounds, FAITHFUL; the reading of the dictated phrase is argued in `request.md` rather than assumed |
| VI (verification before done) | SC-008: `make done` and `make page-check` green |
| X clause 5 (100% coverage) | no engine code changes; the record, the registry and the derived assets only |

## The shape of the work

**The reading is delegated; the WRITING is not.** Constitution XII is explicit that a session writes the
entry from the quotes a reader returns, and feature 143 is explicit that web reading runs in background
agents because one hung fetch blocks the whole turn. So:

1. **Research agents, one per subject**, each given its slice of [`notes-worklist.md`](notes-worklist.md).
   They search, they fetch, they return a verdict per note with any passage verbatim. **They do not edit
   the record.** Their return is the evidence the session writes from, and it is kept in
   `reader-reports.md` so a later reader can check the entry against what was actually returned.
2. **The session writes** each footnote, each registry entry and each corrected sentence.
3. **The checks run on what landed**: `source-applicability` per new key, `quote-check` per changed
   footnote, `record-format` per changed page.

Batching is by SUBJECT rather than by page, because one source usually settles several notes and they
are spread across pages: the canal-sizing question alone is five notes on one page and more on two
others.

| batch | notes | why it is one batch |
|---|---|---|
| water A - canals, ditches, sizing | ~28 | the GB 50288 cluster and the comb-net widths; one standard would settle several |
| water B - moats, ponds, wetland, flow | ~28 | a different literature: hydrology and defense rather than irrigation design |
| funerary and temple | 29 | one literature (Japanese and Chinese religious practice), the largest single-subject block |
| fields and crops | 27 | agronomy and land use |
| buildings and houses | 20 | vernacular architecture and urban form |
| trade works, defense, government | 16 | the urban institutions |
| vegetation, roads, the rest | 14 | what is left, kept together because none is large |

## Order

Phase 1 is the reading, and it is the long pole; every batch runs in the background at once, and the
session writes up each as it returns rather than waiting for all seven. Phase 2 is the checks, which can
only run on text that has landed. Phase 3 is the two artifacts for the GM and the gate.

## Risks, and what is done about each

- **A batch returns thin work.** FR-002's floor is per note and SC-005 is checkable, so a thin return is
  visible in the report rather than in the record. A batch that returns rows without queries or pointers
  is sent back.
- **An agent edits the record.** Every batch prompt forbids it and names the one file it may write.
- **A stall with no notification** (feature 143): a `Monitor` on the stall watcher runs while readers are
  out, and a stalled agent is stopped and relaunched with the failed host excluded.
- **The container.** Seven readers at once are cheap next to a gate; no gate runs beside them.
- **Scope creep into the maps.** FR-004 and the out-of-scope list draw the line, and the closing report
  is where a map that should change gets named instead of changed.
