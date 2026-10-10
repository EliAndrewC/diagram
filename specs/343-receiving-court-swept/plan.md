# Implementation Plan: is the receiving court "swept"? (feature 343)

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

**D1 - The record write** (FR-001): 0104's findings page gains the absence note and the two-drawings sentence, from
research.md R1; written by the shared write session, committed `343: ...`.

**D2 - The modal** (FR-002): `border-court.md` reworded by this session after the record lands (its Entry and Drawing name
0104 and 0110). It owes `modal-form`, `modal-research` and `modal-depiction` (`make record-owed` names them), each from
`make modal-bundle`.

**D3 - The sheet's comments** (FR-005): the three "swept" comments of `ubame-magistracy.svg` reworded. No drawn element
changes, so no review check is owed (feature 294).

**D4 - The implementation check** (FR-004): the claims citing 0104's findings, re-owed by the change, are triaged or
re-checked; a question no code decides is recorded per feature 378.

## Project Structure

```text
research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan{.html,.notes.html}
l7r/diagram/interactive/assets/modals/sheet/border-court.md
pool/magistracies/ubame-magistracy/ubame-magistracy.svg   comments only
```
