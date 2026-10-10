# Implementation Plan: where did the Koseki form's middle gate stand? (feature 338)

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

**D1 - The record write** (FR-001): 0104's findings page states what the Koseki house shows of its middle gate (a gate in
the roji wall, from the gate court to the principal room's veranda; a house with no offices), and an absence note that no
source places a middle gate relative to an office hall. Committed `338: ...` by the shared write session.

**D2 - The drawing page** (FR-002): 0104's drawing page labels the divider gate behind the office hall a GUESS no source
places. The spec's Why is reworded so the silence is not stated as a refutation ("the premise does not hold" becomes
"no source places it").

**D3 - The download list**: the 1994 repair report 『旧小関家住宅修理工事報告書』 goes to `research/to-download.md` through
`make download-add`.

**D4 - The implementation check** (FR-091): the claims citing 0104's findings are re-owed and checked.

## Project Structure

```text
research/questions/0104-the-formal-entrance-and-a-guests-arrival-genkan{.html,.drawing.html,.notes.html}
research/to-download.md   through make download-add
```
