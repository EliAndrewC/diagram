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
  slices it by heading, and on that basis the entry has 181 words, yields 7 candidates and catches **2
  of the eleven proposed terms** (`girder` and `footplank`, both of them core) and **none of the three
  that varied between runs**. R2 measured the fragment plus its notes - 324 words, 34 candidates, 2 of
  the 3 varying terms and 6 of the 8 core - because that is what `record-format` is handed. 27 of the
  34 come from the quoted passages in the notes, and every variance-relevant catch is among them: on
  the assembled basis this feature's own headline number would be 0 of 3. The candidate list must walk
  what the check reads, or it is a list about a different document. (The plan review of 2026-09-20
  measured this line: the "3" here was correct only while the count of 12 included `obliquity`, which
  every run dismissed, and the sweep that replaced "12 known" with "eleven proposed" kept the number
  and made it wrong.)
- **what is defined**: the variant index feature 259 derives.
- **how common a word is**: a document-frequency map over the record's question fragments.
- **the registry keys** (FR-004): matched as a WHOLE TOKEN against `SOURCES.html`'s own key ids, never
  as a substring - `nrcs` is both a registry key's prefix and **one of the three terms whose presence
  varied between feature 259's runs**, which is to say one of the two this list exists to catch, so a
  loose substring test would delete the finding the feature is for. FR-004 has a second half, on the
  same reasoning and in the same place: text inside a `<code>` span is not scanned at all, because a
  span carries a key or an identifier rather than a word a reader is asked to know. Both are FLOORS -
  measured on the entry this was built against, each removes nothing, and R3 records that rather than
  claiming a saving.

It is pure so its test needs no filesystem; the caller reads the four and passes them in.

### D2 - Why the cutoff is 2, stated where it is applied

R2 measured the whole curve: the catch plateaus from a cutoff of 2 onward - 2 of the 3 terms that
varied between runs, 6 of the 8 core - while the list
keeps growing, so 2 is the cheapest cutoff that catches what this filter can catch. The number lives
beside the code that applies it with that measurement, not in a doc.

### D3 - What the filter cannot reach goes in the CONTRACT, not only in the research

Three of the eleven proposed terms are unreachable by a word-level rarity filter (R3): two phrases and one
word the record uses 23 times. If the contract does not say so, an empty list reads as an empty
question - which is exactly the failure mode a mechanical pre-pass introduces. So FR-008 is a contract
change, and it is the one part of this feature that is about the model rather than the script.

### D4 - The acceptance bar moves in the operative doc, and the old specs stay as they are

`research/CLAUDE.md` carries the bar a session reads. Features 258 and 259 keep their specs, including
259's SC-002 recorded as unmet: a spec records what was decided when, and rewriting one to match a
later decision is the yardstick-editing this project refused two rounds ago.

**One other operative doc changes, and only because it states the OLD bar on the SAME decision.**
`docs/efficiency-tooling.md`'s feature-255 row judged candidates that "cut what a check READS" by
whether each "hit every recorded finding for less". Its finding stands and is kept verbatim; its
criterion is the one this feature replaces, so the row gains a pointer to the new bar rather than
standing beside it as a second one (FR-009a). The two survivors named in FR-009a are about a model-TIER
downgrade, a different decision, and are deliberately untouched.

## Phases

**Phase 0 - the baseline** (T01, T02). `make done` on unmodified code; R4's before.

**Phase 1 - the candidate pass** (T03-T06). Red first; the function; the prepass prints it; one entry,
then every entry.

**Phase 2 - what it is for** (T07, T08). The contract and the operative doc.

**Phase 3 - landing** (T09-T12, T11a). The `record-format` run judged by the new bar; `make done`;
R4's after; **the substitution put to the GM** (T11a, FR-011 and SC-007 - it is a numbered step rather
than a closing courtesy precisely so that it cannot be the thing that falls off the end of a long
chain); the push.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| A corpus walk on every prepass invocation | "Rare in the record" cannot be known without the record; caching it to a file would be a derived thing to keep in step, which is what feature 259 spent a review round removing | Shipping a common-word list was rejected because it is external data with its own provenance, and this project's rule is derive rather than maintain. A cached frequency FILE was rejected because the walk is cheap: 0.31 s for the corpus, and 0.83 s for the candidate pass over all 321 sections of the record's 19 question pages (R4, re-measured after the plan review reported a different denominator), against FR-010's five-second bar. The walk is memoized WITHIN a run - four derived inputs read once, not once per page, which took the whole-record sweep from 7.52 s to 0.83 s |
