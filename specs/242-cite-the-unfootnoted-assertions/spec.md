# Feature 242 - cite the unfootnoted assertions

**Status:** specified; awaiting a FAITHFUL verdict (see Review history).

## Summary

Feature 238 read all nineteen research pages with four independent `quote-check` readers, inventoried
**695 sentences** that assert something about how a place was built, farmed, governed or lived in and
carry no footnote (`m:inventory-items`, `research.md` R1), classified every one, and worked every item
that needed no new reading. This feature is the remainder the GM asked for when they said *"close out
all of the low hanging fruit ... and then we can close out this feature and open a successor for the
rest."* It is the deep round: each item needs its own `source-reader` pass before a footnote can be
written.

**The remainder is 462 to 472 items, not the "about 600" feature 238's closing report stated**
(`m:worklist-low`, `m:worklist-high`; `research.md` R1). That figure counted R6 dispositions made
BEFORE 238 converted 142 markers into absence notes, and R7 states that a reader-report item quoting a
marker is thereby closed. The work list is a FILTER over the four reader reports, derived by
`measure/inventory_census.py`, never a number restated from prose.

**A second class of 119 items** carries an absence note whose text says no query was ever run
(`m:absence-notes-never-searched`; `research.md` R2). Those are backlog, not settled questions, and D1
records why this feature owns them.

This feature writes no engine code (D3), so its delta takes the DIRECT route.

## Functional requirements

**FR-001 - the work list is DERIVED from the reader reports, not restated.** The inputs are feature
238's `research.md` R3 (the four shapes), R6 (the classification), R6a (why the counts are the readers'
own) and R7 (the closed list), plus the four verbatim reports under
`specs/238-unfootnoted-assertions-researched/reader-reports/`, which R7 declares the authority on
identity. The list is every item the reports name, less the items whose prose carried a marker (R7
class 1) and less R7 classes 2, 3, 5 and 6 - the fourteen roster-hidden claims, the six sections that
disclosed with no footnote at all, the one `settlements.html` item and the caravan inn.
`measure/inventory_census.py` performs exactly that filter and refuses to report if it cannot reproduce
each report's own stated total. **R7 class 4, the twelve defects, is deliberately not subtracted**: those
were found in the second reading, of material that already carried a footnote, while the four inventory
readers named only assertions carrying none, so the two populations are disjoint by construction. Where
one did coincide, the list is overstated by at most twelve.

**FR-002 - the inventory is not REBUILT; the pages are still opened.** 238 finished the inventory so
this feature would not have to redo it, and the nineteen pages are not re-read end to end to find new
items. This does not exempt the pages from being edited, nor from the checks of FR-007, which read
every changed page.

**FR-003 - a `source-reader` pass runs before any note is written, and the note is written from the
quotes it returns.** No footnote is written from memory, from a search summary, or from another page's
paraphrase. An agent's finding is a lead, not a verdict: 238 recorded two that did not survive checking
(a quotation an agent called differing that the paper confirms, and a CONTRADICTED verdict on a claim
that was in the session's own prompt).

**FR-004 - every worked item ends in exactly one of the three footnote forms.** A **CITATION** carries
the key, a link to a public page, and the passage quoted verbatim from that page - feature 195 requires
both halves, the quote and a page a reader can read it on. An **ABSENCE** note carries no key and no
link and reads `no publicly readable source (searched YYYY-MM-DD: what was tried)`, one date
immediately followed by a colon, which is what the classifier matches. A **GROUNDS** note reads `no
source is owed: <reason>` and its reason comes from the closed list of six - *measured on our own maps*,
*the record's own silence*, *follows from the definitions*, *physical necessity*, *a drawing
convention*, *this project's decision* - and may name more than one. A grounds note may **never** carry
a claim about how a place was built, farmed, planted, governed or lived in, and may **never** carry a
sentence the record labels a GUESS about the physical world; both owe a citation or an absence note
however they are dressed. Feature 238 had a grounds note refused by `quote-check` for exactly the first
prohibition, after writing a warning about that risk into the note's own comment.

**FR-005 - the note lives on the citations page.** The `<li id="fn-n">` goes on
`research/citations/<name>.html` with its back link, the `<sup class="fn">` reference goes at the
assertion on the research page, and `make citations` derives `citations/<name>.js`. A new registry key
carries both write-ups - *What it is* and *Why it applies, and its limits* - before it is cited.

**FR-006 - a contradiction is corrected on the page and recorded, never quietly dropped.** Where a
reading shows the record states something WRONG rather than merely unsupported, the entry is rewritten
to say the finding and the correction is recorded in `research.md`. Nothing in the entry says what it
used to say.

**FR-007 - the checks the changed material owes.** `quote-check` and `record-format` over every changed
page; `source-applicability` over every new registry key, and before its numbers, claims or details
reach a map or a rule.

**FR-008 - every `entry-drift` pair is answered.** Each pair `scripts/_entry_owed.py` names is either
dispatched to the `entry-drift` agent and the modal prose rewritten, or discharged with one recorded
`ENTRY_DRIFT_OK="<reason>"` covering a sweep in which no finding moved.

**FR-009 - the work lands in batches.** A page's items are finished, checked and committed together, so
an interrupted run leaves finished pages rather than a half-noted record.

**FR-010 - the documents that cannot be read are appended to the END of `TO-DOWNLOAD.md` Part 4.** The
GM's condition, in their words: *"you should definitely append them to the end rather than burying them
in the middle so that I will be able to make sure that I get to all of them."* Each entry is a clickable
markdown link - an exact one where it exists, a Google-search link where it does not - and says what
rests on it and what blocked the fetch.

**FR-011 - the completion condition, and what is NAMED rather than absorbed.** The feature is
complete when every item on the FR-001 list **and every item on the D1 list of 119 never-searched
absence notes** carries one of FR-004's three forms, the two counted and reported separately so they
never blur. What the pass cannot close is named in the closing report, and an item that was
**searched and failed** is distinguished from one that was **never searched** - 238's own closing
report warns that most of this remainder has never been searched and that a successor should not
read it as a failed hunt. If the work proves too large to finish, the split is proposed to the GM
with a count rather than taken unilaterally: *"a successor for the rest"* asked for the whole
remainder.

**FR-012 - the order of work is the readers' own confidence labels**, strongest first: HIGH,
MEDIUM-HIGH, MEDIUM, LOW-MEDIUM, LOW. The readers rated the 494 parsed bare items HIGH 222,
MEDIUM-HIGH 24, MEDIUM 207, LOW-MEDIUM 4 and LOW 37 (`m:worklist-high-confidence`,
`m:worklist-medium-high-confidence`, `m:worklist-medium-confidence`,
`m:worklist-low-medium-confidence`, `m:worklist-low-confidence`; `research.md` R1) - the composition of
the bare population BEFORE the twenty-two items R7 closes, so the five deliberately do not sum to
FR-001's 462 to 472. **The two hedged tiers are reported rather than rounded**: the readers hedged
29 of the 695 inventoried items on purpose (`m:hedged-items`), 28 of them in the 494-item bare
population this composition describes (`m:hedged-bare`), and at most 27 on the work list itself
(`m:hedged-worklist-max`; `research.md` R1) - the caravan inn is MEDIUM-HIGH and is one of the
twenty-two R7 closes, and it is the only closure the reports name, so the other twenty-one cannot be
checked for hedges. Collapsing any of them into a neighboring tier would invent a judgment the
readers declined to make.
The reports carry the label per item and R6a records the splits, so the ordering applies to the list as
it stands.

**FR-013 - the fifty-one redundant roster disclosures are rewritten.** Feature 238 R7 handed them over
as tidying: the honest label now sits at the assertion while the section's `Sources:` line still
carries it too. Fifty-one edits, no change of meaning in any.

**FR-014 - the two items only the GM can settle are RELAYED, not built here.** Whether the caravan
inn's story count should become a knob, and the Xuxiebian site name, which a second full search of both
Wagner works confirms is in neither. Building the knob would be engine code and would put this
feature's delta on the GATED route; this feature does not build it.

## Success criteria

- **SC-001** (FR-001, FR-002) - the work list is produced by running `measure/inventory_census.py`, and
  its count is the spec's count; no figure for the remainder appears anywhere in the feature that the
  harness did not produce.
- **SC-002** (FR-003, FR-004) - every footnote the feature adds is one of the three forms, written from
  a returned quote; no grounds note carries a claim about how a place was built, farmed, planted,
  governed or lived in.
- **SC-003** (FR-005) - `make citations` is green and every new registry key carries both write-ups.
- **SC-004** (FR-006) - every contradiction found is corrected on its page and recorded in
  `research.md`.
- **SC-005** (FR-007) - `quote-check` and `record-format` have run over every changed page and
  `source-applicability` over every new key, with the verdicts recorded in the task.
- **SC-006** (FR-008) - `scripts/_entry_owed.py` names no unanswered pair at push.
- **SC-007** (FR-009) - every commit leaves the record in a state a reader could read.
- **SC-008** (FR-010) - Part 4 of `TO-DOWNLOAD.md` has grown only at its end, and every entry is a
  working link.
- **SC-009** (FR-011) - the closing report states, per unclosed item, whether it was searched and
  failed or never searched.
- **SC-010** (FR-012) - no item is worked while an item of a stronger tier is open, over the whole tier
  order HIGH, MEDIUM-HIGH, MEDIUM, LOW-MEDIUM, LOW, absent a stated reason.
- **SC-011** (FR-013) - no section's `Sources:` roster carries a disclosure that its own notes now
  carry.
- **SC-012** (FR-014) - the feature's delta contains no `l7r/**/*.py` change, and both GM items appear
  in the closing report as relayed questions.
- **SC-013** (FR-011) - the 119 never-searched absence notes are worked and counted separately from
  the FR-001 list, and neither count is folded into the other in any report.
- **SC-014** (spec-wide) - `make page-check` green and the push clean.

## Decisions recorded

**D1 - an absence note that records no search is IN scope.** 119 of the record's 259 absence notes say
no query of its own was run (`m:absence-notes-never-searched`; `research.md` R2). The narrow reading
would put them out of scope, because they carry a footnote and the GM's population was assertions that
*"do not carry a footnote"* - and it was priced: it makes the feature about a quarter smaller and
leaves 119 assertions permanently labeled unsearched with nothing scheduled to search them.
The doctrine settles it: `research/CLAUDE.md` lets an absence note leave the backlog only by carrying
`settled DATE` after **two independent passes on different dates**, and none of the 119 has had even
one - each says in so many words that no query of its own was run. An unsettled absence note is
backlog by definition, and feature 232's second pass found readable sources for 90 of 162 notes a
first pass had called absent, so the expected yield is not small. They are worked after the FR-001
list; FR-011 makes them part of the completion condition rather than an intention recorded only here,
and both counts are reported separately so the two classes never blur.

**D2 - "does not re-read the record" means the inventory is not rebuilt.** Feature 238's FR-013 grants
exactly that and no more. The pages are still opened to place footnotes and are still read by
`record-format` and `quote-check`. Stated because the draft this replaces said flatly *"It does not
re-read the record"*, which a session could read as license to skip FR-007.

**D3 - this feature is research-only and takes the DIRECT route.** Nothing in FR-001 to FR-013 touches
`l7r/**/*.py` or a pool generator. FR-014 is what keeps it that way: the caravan-inn knob is the one
inherited item that would be engine code, and it is relayed rather than built. If the GM asks for the
knob, that is a separate feature with its own gate and pool sweep, or an amendment to this one whose
route consequence is stated when it is made.

**D4 - the ordering is confidence, not corrected-wrongness.** Feature 238's draft proposed working the
items the record states WRONGLY first. Nothing in the reports or in R6 marks an item as wrong rather
than unsupported - that class was found by reading, and FR-002 forbids the reading that would find it -
so the rule could not be applied. The readers' HIGH/MEDIUM/LOW labels are carried per item and are used
instead (FR-012).

**D5 - the fifty-one roster disclosures are worked here rather than deferred a second time.** Feature
238 deferred them by volume and named them, as its FR-012 required. Repeating "deferred by volume" in
the successor would defer them to nowhere, so FR-013 makes them work.

## Review history

- **Round 1 (2026-09-13), `spec-fidelity`: CHANGES REQUIRED**, nine items against a draft outline that
  had no requirements, no success criteria and no completion condition. All nine applied: the scope
  figure replaced by a derived one and the contradiction with the spec's own inputs removed (item 1,
  FR-001 and `research.md` R1); the fifty-one roster disclosures made work rather than a second
  deferral (2, FR-013 and D5); a completion condition and the searched-versus-never-searched
  distinction added (3, FR-011); feature 238's FR-003 to FR-010 obligations carried forward as
  requirements (4, FR-003 to FR-010); the grounds-note closed list quoted in full at six reasons rather
  than four, with the second prohibition restored (5, FR-004); the unactionable ordering rule replaced
  by the readers' own confidence labels (6, FR-012 and D4); the caravan-inn knob stated as relayed with
  its route consequence (7, FR-014 and D3); "does not re-read the record" narrowed to "the inventory is
  not rebuilt" (8, FR-002 and D2); and the housekeeping - Status line, `R<k>` and `m:` pointers on every
  measured figure, an SC naming every FR (9).
- **Round 2 (2026-09-13), `spec-fidelity`: CHANGES REQUIRED**, three items, on a review that re-ran both
  harnesses and confirmed every figure. All three applied: FR-011's completion condition now covers the
  D1 list, which the Summary claimed and no requirement carried, with SC-013 to hold it (1); FR-001 now
  names the R7 classes the filter actually subtracts, the harness subtracts the caravan inn as well, and
  the twelve defects are stated as disjoint rather than silently skipped, moving the count to 462 to 472
  (2); FR-012's confidence figures are stated as the composition of the 494 parsed bare items before
  R7's twenty-two closures, so they no longer read as a work list that does not sum (3). The review
  upheld D1 as a defensible reading and offered a stronger ground for it, which D1 now takes. Both
  asides applied: the stray empty `reader-reports/` directory is removed.
- **Round 3 (2026-09-13), `spec-fidelity`: FAITHFUL**, on a review that re-ran both harnesses, checked
  every `m:` key against the fresh output, verified the arithmetic closes (on round 3's own run,
  222 + 231 + 41 = 494, less R7's 22 = 472) and independently confirmed the disjointness argument by
  reading
  R7 class 4's five sources - every one of the twelve corrections is in footnoted material or a
  registry write-up, while the inventory names only assertions carrying no footnote.
- **After acceptance (2026-09-13), one figure corrected, counter reset per the GM's 2026-09-12
  rule.** Round 3's closing aside supposed a single item carried a hyphenated confidence label;
  counting found **29 of the 695 inventoried items** (`m:hedged-items`) - 25 MEDIUM-HIGH and 4
  LOW-MEDIUM, 28 of them bare (`m:hedged-bare`) and at most 27 on the work list
  (`m:hedged-worklist-max`) - every one of which the parser was bucketing a tier low, a MEDIUM-HIGH
  into MEDIUM and a LOW-MEDIUM into LOW, so FR-012's ordering would have met all 28 of the bare ones
  later than the readers meant. The harness now reports the readers' hedged labels as their own
  tiers instead of rounding them, and FR-012 states five tiers rather than three. The work list
  itself does not move: the compound labels never affected which items are on it, only the printed
  composition.
- **Round 4 (2026-09-13), `spec-fidelity`: CHANGES REQUIRED**, two items, on a review that re-ran the
  harness, confirmed the five tiers sum to 494 with the work list unmoved, and established that item
  selection could not have moved because `items()`' own label regex is byte-identical in the diff. Both
  applied: FR-012 said "29 items" of a paragraph whose declared population is the 494 bare, where the
  count is 28, so both figures are now qualified by the population they belong to (1); and SC-010 named
  two of five tiers, so working a MEDIUM item while a MEDIUM-HIGH item was open would have satisfied it
  while breaking FR-012 - exactly the boundary this change exists to fix - and it is restated over the
  whole tier order (2). The review's aside is fixed too: `confidence()` normalized a reversed compound
  to a name outside `TIERS`, which would have dropped such an item from every printed share while the
  totals still looked right; it now normalizes correctly, and the run FAILS on any tier outside `TIERS`
  or a composition that does not sum to the bare count, rather than printing a plausible wrong split.
- **Round 5 (2026-09-13), `spec-fidelity`: CHANGES REQUIRED**, three items. The first two were one
  mistake made twice: "28 of them on this list" attached the BARE population's hedged count to the
  work list, when the caravan inn is itself hedged, bare and one of the twenty-two closures, so at
  most 27 are listed; and "met 24 listed items later" counted only the MEDIUM-HIGH tier while claiming
  "every one of which", when reading the first word demoted the 4 LOW-MEDIUM items into LOW as well.
  **The third item is why the first two survived a round that re-ran every other figure**: the hedged
  counts lived only in prose, so no instrument produced them and `make figures` had nothing to check.
  The harness derives and records all three now (`m:hedged-items`, `m:hedged-bare`,
  `m:hedged-worklist-max`) and prints them beside the tier line, and its unrecognized-tier refusal was
  widened from the bare items to every item, since the 29 is taken over all 695 and a stray tier on a
  marked item would corrupt a recorded figure just as quietly. The round-3 arithmetic carries its "on
  round 3's own run" label.
- **Round 6**: pending.
