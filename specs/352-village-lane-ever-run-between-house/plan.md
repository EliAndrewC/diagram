# Implementation Plan: did a village lane ever run between a house and its own grove? (feature 352)

**Spec**: `spec.md` | **Request**: `request.md`

## Summary

A research-record feature: one question searched and its answer or absence recorded on 0036, then the code that keeps lanes
off a household's wood share tagged against that finding, each claim judged by `impl-drift`. No map changes.

## Technical Context

- **The record.** Written and checked by FRESH page sessions from briefs (`make page-session BRIEF="m1-write.md
  m1-check.md"`): one write session (the search pass, archive first, and the record on 0036), one check-and-apply session.
  One question; new registry keys only where a source is found and cited.
- **The claims.** The ten claims FR-003 lists, found by its recorded search over the claims index's keys and notes and
  the `Research:` claim text in the code (its five exclusions stated there). Their claims are
  edited in this session after the record lands (a docstring's `Research:` lines - no engine line), then bundled with
  `make claims-bundle` and judged by `impl-drift`; `make claims-checked` records the verdicts.

## Performance bookends

N/A: no generator change (FR-004).

## Constitution Check

- **I-V, VI**: N/A.
- **XII (research)**: the search runs the archive before the web; China first, Japan as tiebreaker; every assertion
  footnoted to a quoted passage, or an absence note naming the search.
- **XIII**: tooling tests and the gate green.
- **XVI**: built as written; a DRIFTED claim is recorded, the code not changed (FR-004).

## Decisions

**D1 - The search and the record** (FR-001, FR-002): the write session searches the archive (`make archive-find`) and then
the web, in Chinese and Japanese, for whether a lane or path ran between a farmhouse and its own homestead grove or dooryard
copse, and records on 0036's findings page, under a heading a reader would ask, the answer with footnoted passages or an
absence note naming each search. Its drawing page says how our maps settle it (the copse seats reserved and kept off by
lanes, feature 287 woods W25).

**D2 - The checks** (FR-002): `make record-owed` after the write; the check session dispatches every owed unit from its
bundle (source-reader, quote-check, record-format, source-applicability for a new source) and answers each.

**D3 - The claims** (FR-003): each claim FR-003 lists is rewritten to cite 0036's findings page (keeping the pages it cites
now) and to say what the code does in the finding's terms; where the finding does not reach a claim's detail (a buffer's
distance), the claim stays a labeled guess citing 0036's absence. `make claims-bundle UNITS=...` (or `OWED=1`) and one
`impl-drift` pass; MISLABELED is relabeled and re-checked; DRIFTED is recorded.

**D4 - What no code decides** (FR-003, FR-005): if no unit keeps a lane out of the gap between a house and its own seats,
`implementation-check.md` records it as implemented nowhere, with the search (the recorded command and a grep over the
seating and the ways for the house-to-seat gap). `make impl-check F=352` reports nothing missing.

## Project Structure

```text
research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.html
research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.notes.html
research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.drawing.html
l7r/diagram/overlap/reserved.py                       a docstring's claims
l7r/diagram/hamletgen/homesteads/household_ways.py    a docstring's claims
l7r/diagram/hamletgen/homesteads/region.py            a docstring's claims
l7r/diagram/hamletgen/homesteads/stages.py            a docstring's claims
l7r/diagram/hamletgen/homesteads/growth.py            a docstring's claims
l7r/diagram/hamletgen/ways/track.py                   a docstring's claims
l7r/diagram/hamletgen/ways/web.py                     a docstring's claims
l7r/diagram/settlement/rolling/gap_ways.py            a docstring's claims
l7r/diagram/settlement/rolling/passage.py             a docstring's claims
l7r/diagram/settlement/homestead_parts/wood_share.py  a docstring's claims
specs/352-village-lane-ever-run-between-house/briefs/  m1-write.md, m1-check.md
```
