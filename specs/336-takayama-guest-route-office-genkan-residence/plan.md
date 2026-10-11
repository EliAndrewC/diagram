# Implementation Plan: did Takayama's guest route run indoors? (feature 336)

**Spec**: `spec.md` | **Request**: `request.md` | **Research**: `research.md`

## Summary

A research-record feature: the finding written into the record, its checks answered, and its implementation check.
Every task is `research: physical` for the record write; the rest `research: rendering`.

## Technical Context

- **The record.** Its edits are made by a FRESH page session from a brief (`make page-session`), shared by features 336,
  337, 338 and 343: one write session, then one check-and-apply session, as the record's process requires. The session
  makes ONE COMMIT PER FEATURE, its subject opening with the feature's number, so `make impl-check` attributes each
  change.
- **The claims.** Through the existing claims commands (`make claims-owed`, `claims-bundle`, `claims-checked`, the
  triage) and feature 378's `make impl-check`.

## Performance bookends

N/A: no generator change.

## Constitution Check

- **I-V, VI**: N/A.
- **XII (research)**: the finding is recorded with its sources and limits; the record checks it owes are answered.
- **XIII**: tooling tests green.
- **XVI**: built as written.

## Decisions

**D1 - The record write** (FR-001): 0104's findings page carries the three Takayama sources with their limits (the
visitors' route, the 渡廊下 in the facility table, and the official illustration of office and residence under joined
roofs), each from research.md R1 and R2. Committed `336: ...` by the shared write session. The illustration is cited by
its page, https://jinya.gifu.jp/en/architecture/, which shows it.

**D2 - The download list**: the 1830 drawing the 1996 restoration followed goes to `research/to-download.md` through
`make download-add`.

**D3 - The claim on the route's code** (FR-002). `_roji_parts` in `l7r/diagram/compound_parts.py` is the code that sends a
guest out of doors: "from the middle gate a stepping-stone path, the roji, straight to a shoe stone at the reception room's
veranda". It gains a `Research:` claim citing 0104's findings page, in its docstring, and its `impl-drift` check is to
record it DRIFTED. `STONE_STEP_FT` only spaces the stones and is not the decision (plan review, round 1). The
statement behind it at `compound_model.py` (the `DOOR_KINDS` comment: "the guest's way is the middle gate and the roji ...
so the residence carries no genkan") is a comment the claims grammar cannot read; it is reworded to point at the claim.
The unit enters the index through feature 378's claimed-outside rule. The edit is a docstring and a comment, not code.

**D3a - Ochiba's own route is drawn by no code, and its mismatch is recorded where a hand sheet's can be.** The Ochiba
sheet is hand-authored SVG (`ochiba-magistracy.gen.py` only rasterizes it); `claims.py` reads no SVG. The feature's
`implementation-check.md` line for Ochiba states:
- that the sheet's outdoor route (the office's rear door, the nakamon, the garden path to the veranda stone, which its own
  svg comment cites to research 0104 and Takayama) departs from 0104's finding that the way ran under roof - the mismatch
  FR-002 names;
- that `_roji_parts`'s DRIFTED claim is its checked counterpart for the generated route;
- that the sheet stays untouched (FR-002, FR-091).

**D4 - The implementation check** (FR-091): `make impl-check F=336` reports nothing missing.

## Project Structure

```text
research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.html
research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan.notes.html
l7r/diagram/compound_parts.py   the claim on _roji_parts (docstring)
l7r/diagram/compound_model.py   the DOOR_KINDS comment points at it
research/to-download.md   through make download-add
```
