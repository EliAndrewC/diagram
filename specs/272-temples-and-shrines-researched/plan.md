# Implementation Plan: 272 - temples and shrines researched

**Branch**: none (`export SPECIFY_FEATURE=272-temples-and-shrines-researched`) | **Date**: 2026-09-27 | **Spec**: [spec.md](spec.md)

## Summary

Research recorded on `religion-and-death`: a second search behind every absence note and labeled guess in 010-128
and 210's shrine and temple parts; new questions for the town monastery and the town and city shrine (450-490), the
village temple and wayside shrines (500-540), the state cult and temple plans (550-570), the city temple complex and
the temple neighborhood (580-590) and the city temple's clergy, gate shops and graveyard (310-330); every
human-fetchable source on the GM's download list; every entry checked; a finding that contradicts the Hoshigaoka
country shrine applied to its sheet and map.

## Technical context

- **Surface**: `research/religion-and-death/` fragments and notes, `research/sources/` registry entries, the
  glossary, the assembled pages (`make record`, `make citations`); `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`
  (appended, never git); the claims file and the two inventories. The Hoshigaoka sheet and frozen map only if a
  finding contradicts them (FR-007).
- **No engine change** is planned; the route at push is DIRECT unless FR-007 moves the sheet's generator.
- **Tooling reused, not built**: 271's brief generator and queue (`briefs/gen.py`, `briefs/queue.sh`, adapted),
  `scripts/page-session.sh`, `scripts/pull-queue.sh`, `make check-bundle`, `make apply-edits`, `make reserve`.

## Constitution check

- I-V, VII, VIII: N/A - no UI, no pool roll, no SOURCE blocks, no in-world prose.
- VI: PASS - the record checks per entry (FR-004); `make done` at the end.
- IX: PASS - the GM's canon (`make canon`) governs the setting; the history is reported against it.
- X: PASS - the record's own tests (footnotes, citations, sources, record format, question size) per session.
- XII: PASS - this feature IS the search pass; every outcome labeled.
- XIII: PASS - baseline main's green gate; no roll moves.
- XVI: PASS - the GM's four objects (shrine gaps, town monasteries, city temple complexes, the small temple and
  shrine of a temple neighborhood) are each a group below.

## Decisions

- **D1 - readers first, then writers.** Eight sonnet readers searched every item on 2026-09-27; their reports are
  in `readers/`. They are LEADS: a writer cites only what `source-reader` returns READ. Class: process.
- **D2 - six groups**, each a write session then check sessions (two questions each), fresh contexts, from briefs:
  S (the 090-128 gaps, D50, D51, the COVERED rows confirmed), R2 (450-490), R4 (550-570), B37 (310-330 and edits to
  010, 050, 070), R3 (500-540), T (580-590 and the 010-070 and 210 notes). The number ranges keep the groups apart on
  one page; 130-206 and 270-300 are 269's and are cited only; 204 waits for 269's R1.
- **D3 - three queue clones** (`.clones/diagram-shrines-1..3`), so three groups run at once without sharing a git
  index: queue 1 runs S then B37, queue 2 runs R2 then R4, queue 3 runs R3 then T (it starts when their readers
  return). `scripts/pull-queue.sh <n>` brings each back; the assembled pages are rebuilt, never merged by hand.
- **D4 - blocked sources**: each writer retries its reader's blocked list once with `curl` (a PDF through
  `pdftotext`) before it becomes a TO-DOWNLOAD entry - three readers reported PDFs their fetch tool could not open.
- **D5 - FR-007**: group S's handoff states, finding by finding, whether it contradicts the Hoshigaoka sheet or map;
  this session applies what does (the 268 layout scripts, the pack audit, `matches_map`, size-audit and
  building-review) or records each as not contradicting in tasks.md.
- **D6 - FR-005**: each group's outcome is written into 271's State table (R2, R3, R4, the D rows) and 269's
  inventory (B37) once it lands, and reported to "Diagram supplemental" and "Diagram research".

## Phases

1. T01: briefs and queues. 2. T02-T07: the six groups, written and checked. 3. T08: FR-007. 4. T09: inventories,
handoffs. 5. T10: `make done`, push.
