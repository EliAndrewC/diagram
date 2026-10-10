# Implementation Plan: loose ends in the privy record (0047), and two of 0006's (feature 368)

**Spec**: `spec.md` | **Request**: `request.md`

## Summary

A research-record feature: five record defects fixed on two questions, their checks answered, and the implementation
check. The record edits are `research: physical` where they touch a quotation (items 2, 3); the rest `research: rendering`.

## Technical Context

- **The record.** Edits made by FRESH page sessions from briefs (`make page-session BRIEF="m2-write.md m2-check.md"`): one
  write session for 0047 and 0006, one check-and-apply session. Two questions, no new registry key expected.
- **The figures.** `measure/privy_reach.py` over the five pool hamlets' recorded manifests; its output
  `measure/privy-reach.txt` is the page's source (FR-001). The script is the feature's, kept in its directory.
- **The stroke.** The dry plot's outline is drawn at `l7r/diagram/settlement/fields/comb.py` (the dry-crop polygon,
  stroke `#A98C58`, width 1.4); the write session reads it there and in the plot builder (`waterfields/carve.py`) for
  what the seam between two plots is (FR-005).

## Performance bookends

N/A: no generator change.

## Constitution Check

- **I-V, VI**: N/A.
- **XII (research)**: the figures are measured on today's maps and the method stated; quotations re-read on the paper.
- **XIII**: tooling tests green.
- **XVI**: built as written; the code is not changed (FR-007).

## Decisions

**D1 - Item 1** (FR-001): 0047's drawing page gives `measure/privy-reach.txt`'s figures and its method (privies only;
center to center, not the engine's corner-to-wall reach; the house's own frame; the half-degree tolerance). The August
table stays whole and dated, apart from today's rows; the "15 of 86" run is marked an unrecorded August run. Every share
statement (the lead's "fewer than half", the table, the paragraph, the bullet) agrees.

**D2 - Items 2 and 3** (FR-002, FR-003): the Kyoto PDF read for p.2242's spelling (the archive first); both copies of
`wang-ochiai-2022-5` set to it. `wang-ochiai-2022-2`'s "Type V1" glossed from the paper's definition if it stands
there, else cut at the "...". Both owe quote-check.

**D3 - Items 4 and 5** (FR-004, FR-005): 0006 gains a visible clause pointing to 0033's holdings; its drawing page says
what the dry plot's stroke stands for at the outer edge and at the seam, and whether it is drawn wider than real, read
from the code in Technical Context.

**D4 - The checks** (FR-006): `make record-owed` after the write; every owed unit dispatched from its bundle by the check
session (quote-check, record-format, entry-drift, and the depiction checks of 0006's modals).

**D5 - The implementation check** (FR-007): the claims citing 0047's and 0006's findings, re-owed by the change, are
triaged or re-checked with `impl-drift`; a claim the new figures contradict is recorded DRIFTED, the code unchanged.

## Project Structure

```text
research/questions/0047-farm-privies-and-their-night-soil-benjo{.html,.notes.html,.drawing.html,.drawing.notes.html}
research/questions/0006-dry-fields-and-their-crops-hatake{.html,.drawing.html}
specs/368-record-0047-loose-ends/measure/   the script and its output
```
