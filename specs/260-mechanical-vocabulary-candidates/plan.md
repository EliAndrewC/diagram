# Implementation Plan: The prepass names the words; the model rules on them

**Feature**: `260-mechanical-vocabulary-candidates` | **Date**: 2026-09-20 | **Spec**: [spec.md](spec.md)

**Input**: [spec.md](spec.md), the GM's choice in [request.md](request.md), the measurements in
[research.md](research.md).

## Summary

One function and three places that use it. `scripts/_record_prepass.py` gains a candidate pass: the
words of a section's visible text that have no line in `glossary-variants.txt` and appear in at most 2
of the record's question fragments, each with its count. `record-format`'s contract gains the rule that
it rules on every one. `research/CLAUDE.md` gains the acceptance bar that replaces "the same findings".

It is small because feature 259 built the thing it needs: the variant index is the membership test, and
the record's fragments are the corpus. Nothing is shipped and nothing is maintained by hand.

## Technical Context

**Language/Version**: Python 3.11. **Primary dependencies**: none new.

**Storage**: none. The corpus is derived at run time from the fragments already on disk.

**Testing**: pytest in the tooling tree, where the prepass's own tests live.

**Performance**: the corpus walk reads 1,479 files once per invocation; FR-010's bar is 5 s, measured
in R4.

**Constraints**: the prepass prints; it decides nothing and edits nothing.

**Single-artifact target**: the entry feature 259 measured three times, `ways` 010 - so this feature's
numbers are comparable with that feature's.

**Every step is two steps**: the candidate pass on that one entry, then over every entry of the record
(T05, T06).

## Performance bookends

**N/A - no generator changes.** No map is drawn. The cost this feature can add is to the prepass, which
R4 measures, and to the gate, which it does not touch.

## Constitution Check

- **I, II, III, VII, VIII, IX**: N/A - no UI, no map style, no pool content, nothing generated about a
  place, no in-world prose, no setting detail moved.
- **IV, V**: **PASS** - no SOURCE block is touched; `request.md` is written once from the GM's words.
- **VI. Verify Before Reporting Done**: **PASS** - every task names its verification, and T09 is a real
  `record-format` run judged by the new bar rather than the old one.
- **X. Python Discipline (NON-NEGOTIABLE)**: **PASS** - ruff, ruff format, pyrefly, 100% on what lands,
  red-green on the candidate function. The whole change is under 100 lines in one script.
- **XII. Historical Grounding**: **N/A** - no assertion about the world changes; no research text is
  edited. The feature changes what a script prints.
- **XIII. No Known Regressions**: **PASS with a measured baseline** - `make done` on unmodified code,
  recorded as `m:baseline-done` (R4).

## The design

### D1 - The candidate pass, its four inputs, and WHICH text it walks

`rare_words(text, defined, frequency, cutoff=2, keys)` is a pure function over four inputs, and every
one already exists on disk:

- **the text**: the question fragment AND its `.notes.html`. This is the correction the plan review of
  2026-09-20 blocked on, and it is worth stating plainly: the prepass parses the ASSEMBLED page and
  slices it by heading, and on that basis the entry has 181 words, yields 7 candidates and catches 3 of
  the 12 known terms. R2 measured the fragment plus its notes - 324 words, 34 candidates, 9 of 12 -
  because that is what `record-format` is handed. 27 of the 34 come from the quoted passages in the
  notes. The candidate list must walk what the check reads, or it is a list about a different document.
- **what is defined**: the variant index feature 259 derives.
- **how common a word is**: a document-frequency map over the record's question fragments.
- **the registry keys** (FR-004): matched as a WHOLE TOKEN against `SOURCES.html`'s own key ids, never
  as a substring - `nrcs` is both a registry key's prefix and one of the nine terms the list must
  catch, so a loose test would delete a finding.

It is pure so its test needs no filesystem; the caller reads the four and passes them in.

### D2 - Why the cutoff is 2, stated where it is applied

R2 measured the whole curve: the catch plateaus at 9 of 12 from a cutoff of 2 onward while the list
keeps growing, so 2 is the cheapest cutoff that catches what this filter can catch. The number lives
beside the code that applies it with that measurement, not in a doc.

### D3 - What the filter cannot reach goes in the CONTRACT, not only in the research

Three of the twelve known terms are unreachable by a word-level rarity filter (R3): two phrases and one
word the record uses 23 times. If the contract does not say so, an empty list reads as an empty
question - which is exactly the failure mode a mechanical pre-pass introduces. So FR-008 is a contract
change, and it is the one part of this feature that is about the model rather than the script.

### D4 - The acceptance bar moves in the operative doc, and the old specs stay as they are

`research/CLAUDE.md` carries the bar a session reads. Features 258 and 259 keep their specs, including
259's SC-002 recorded as unmet: a spec records what was decided when, and rewriting one to match a
later decision is the yardstick-editing this project refused two rounds ago.

## Phases

**Phase 0 - the baseline** (T01, T02). `make done` on unmodified code; R4's before.

**Phase 1 - the candidate pass** (T03-T06). Red first; the function; the prepass prints it; one entry,
then every entry.

**Phase 2 - what it is for** (T07, T08). The contract and the operative doc.

**Phase 3 - landing** (T09-T12). The `record-format` run judged by the new bar; `make done`; R4's
after; the push.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| A corpus walk on every prepass invocation | "Rare in the record" cannot be known without the record; caching it to a file would be a derived thing to keep in step, which is what feature 259 spent a review round removing | Shipping a common-word list was rejected because it is external data with its own provenance, and this project's rule is derive rather than maintain. A cached frequency FILE was rejected because the walk is cheap: 0.31 s for the corpus, and 0.79 s for the candidate pass over all 321 entries of the record (R4), against FR-010's five-second bar. The walk is memoized WITHIN a run - four derived inputs read once, not once per page, which took the whole-record sweep from 7.52 s to 0.79 s |
