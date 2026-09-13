# Feature 242 - research notes

## R1 - how big "the rest" actually is, derived rather than restated (2026-09-13)

<!-- The measurement harness is measure/inventory_census.py and measure/note_census.py; every figure
     below is a key in measurements.json, re-derivable with `--record`. -->

Feature 238's closing report put this feature's remainder at "about 600 `CITE` items", taken from its
R6 disposition count of 631. **That number is too large, because it counts items 238 then closed.** R6
classified every one of the 695 inventoried sentences BEFORE the work was done; 238 went on to convert
142 inline markers into absence notes at their own assertions, and R7 states the consequence plainly -
*"A reader-report item whose entry quotes a marker is therefore closed, and that is the largest single
class"* - without ever restating the total.

**The derivation.** R7 declares the four reader reports the authority on identity, so the work list is
a filter over them: every item the readers named, less the items whose prose carried a marker, less
the classes R7 closed by hand. `measure/inventory_census.py` performs it.

The parser's own credibility is the first thing it checks: it reproduces **695** items
(`m:inventory-items`) and every one of the four per-report totals the reports state - 171, 203, 153,
168 - and refuses to report anything if one of them disagrees. The reports use three different item
shapes, and getting all four to their stated totals is what makes the marker split worth reading at
all.

**The answer: 463 to 473 items** (`m:worklist-low`, `m:worklist-high`), against the closing report's
"about 600". The range is honest rather than decorative: the parser classifies 201 items as carrying a
marker where the readers' own stated splits total 211, a disagreement of 10 (`m:marker-classifier-disagreement`),
and the wider bound is the one to plan with. Twenty-one further items are closed in a class other than
the marker conversion - the nine roster-hidden claims on `urban-features`, the five on `buildings`, the
six sections that disclosed with no footnote at all, and the one `settlements.html` item that restates
footnoted canon.

Of the parsed remainder, the readers rated **222 HIGH, 231 MEDIUM and 41 LOW**
(`m:worklist-high-confidence`, `m:worklist-medium-confidence`, `m:worklist-low-confidence`). That split
is the ordering this feature works in, and it replaces the ordering feature 238's draft proposed - "a
claim the record states WRONGLY costs a reader more than one it states without support" - which cannot
be applied, because nothing in the reports marks an item as wrong rather than unsupported. That class
was found by READING, and this feature is told not to re-read.

## R2 - the second class: an absence note that records no search (2026-09-13)

`measure/note_census.py` counts what the record's footnotes are actually made of, over the nineteen
citations pages: **994 citation notes, 259 absence notes and 2 grounds notes** (`m:citation-notes`,
`m:absence-notes`, `m:grounds-notes`).

Of those 259 absence notes, **119 say in so many words that no query of its own was run**
(`m:absence-notes-never-searched`), leaving 140 that record a real search. The 119 are 238's marker
conversions where the marker recorded no reason: the label moved to the assertion honestly, but no
hunt was ever made for it.

**This matters because it decides the feature's size**, and the two readings differ by a quarter. On
the narrow reading the work list is R1's 463 to 473 bare items and those 119 are done, because they
carry a footnote and the population the GM named was assertions that *"do not carry a footnote"*. On
the wider reading they are backlog: `research/CLAUDE.md` says an absence note *"re-opens on anything
that changes what can be read"*, and a note that was never searched has nothing to re-open FROM. The
spec takes the wider reading and records why, with the narrow one priced, as decision D1.

<!-- The census counts research/citations/*.html only. citations/<name>.js is DERIVED from the page by
     `make citations`, so a grep over both doubles every figure, which it did on the first attempt. -->
