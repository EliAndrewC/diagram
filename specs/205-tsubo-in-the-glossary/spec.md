# Feature 205 - tsubo in the glossary

**Status**: DRAFT - awaiting `spec-fidelity`.
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Research**: [`research.md`](research.md) - what the record already says a tsubo is.
**Predecessors**: feature 134 (the glossary: every occurrence of a listed term in a modal's
explanation is a hover tooltip); 159 (the last term added, shitsuden).

## Summary

The GM: add *"tsubo"* to the list of words the HTML map's modals define with a hover tooltip. The
list is `l7r/diagram/interactive/glossary.py`; the threshing yard's explanation uses the word three
times and no entry defines it. One entry is added, its definition written from the research record
the explanation cites, and the page does the rest - the tooltip machinery is feature 134's and is
not touched.

## Functional requirements

- **FR-001** `GLOSSARY` gains the term `tsubo` (variant `tsubo`; the word is its own plural), with a
  one- or two-sentence definition written from the record: the Japanese unit of area, a square about
  six feet on a side, the floor of two straw mats laid side by side, about 3.3 square meters (36
  square feet); house floors and work yards were counted in it.
- **FR-002** Every occurrence of the word in a modal's explanation becomes a hover tooltip carrying
  that definition, exactly as feature 134 does for the other terms - the threshing yard's modal today,
  and any explanation that uses the word later.
- **FR-003** Nothing else changes: no other glossary entry, no explanation text, no page script or
  stylesheet. The definition follows the house style (hyphens, American spellings).
- **FR-004** The existing glossary test (`test_the_glossary_is_well_formed_and_used`) proves the term is
  used by a present explanation and well formed; a unit test proves `glossary_for` returns the entry
  for an explanation that uses the word, and not for one that does not.

## Success criteria

- **SC-001** The rendered page of a hamlet (Inashiro, the reference) carries the `tsubo` entry in its
  glossary payload, and the threshing-yard modal's three occurrences are wrapped as tooltips.
- **SC-002** `make done` green; landed GATED (the glossary is engine Python).

## Decisions Recorded

- **D1 - the definition is written from the record, not from general knowledge.** The record's
  Kitamoto passage gives two mats to the tsubo, and its Nishidani passage gives the mat as 3 by 6
  shaku (90 x 180 cm); two of those side by side are one ken square, about 3.3 sq m - which is the
  59.5 sq m the yard explanation quotes for 18 tsubo. Historically accurate; the pointer is
  `research/homesteads.html`, "How big was the work yard, and how did the sizes spread?", footnotes 12
  and 15.
- **D2 - one variant.** "tsubo" is used as its own plural in the prose and in the sources' English, so
  no `tsubos` variant is listed; the compound `tsuke-tsubo` appears only in the research record, never
  in an explanation, and would not match whole-word anyway.
