# Implementation Plan: how big was a roofed hearing court? (feature 337)

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

**D1 - The absence note** (FR-001): 0099's findings page gains an absence note on the roofed court's size, naming ONLY
what R1 records as searched: the record, the archive, Takayama's official and city pages, Japanese Wikipedia's お白洲,
and the Edo, Sado and Suibara coverage. imidas and kotobank are dropped, because R1 does not record them (spec review
note). Written by the shared write session, committed `337: ...`.

**D2 - The Why's "49 mats"** is struck from the spec: R1 does not carry it (spec review note).

**D3 - `make open-questions`** must list it (SC-001): the note's form is the one `open-questions` reads.

**D4 - The implementation check** (FR-091): the claims citing 0099's findings (`ROOFED_ZONES` in `compound_model.py` and
the procedure sections) are re-owed and checked.

## Project Structure

```text
research/questions/0099-the-hearing-court-shirasu{.html,.notes.html}
```
