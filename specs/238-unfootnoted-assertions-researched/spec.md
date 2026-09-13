# Feature 238 - the unfootnoted assertions, researched

**Status:** FAITHFUL (`spec-fidelity`, round 2 of 2, 2026-09-12) - IMPLEMENTING

## Summary

Every sentence on a research page that asserts something about how a place was built, farmed, planted,
governed or lived in owes a footnote. Feature 232 closed the ABSENCE notes; the sentences that carry no
note at all were named as residue and left standing. This feature works that residue: find each one,
research it, and give it one of the three footnote forms the record now has - a CITATION, an ABSENCE
note, or a GROUNDS note (feature 235). Documents no client here can read are appended to the GM's
download list as they are found.

The count is the residue's own estimate of roughly 180 sentences and is not treated as a target: the
inventory this feature builds is the number, and it may be larger or smaller. A measured census of the
pages (`research.md` R1) found 864 paragraphs carrying no footnote across nineteen pages, most of which
are not assertions about the world at all - they are framing, drawing conventions, and recorded
decisions - so the inventory's first job is to separate the ones that owe a note from the ones that do
not. R1 also finds 285 inline `(unsourced)`-class markers, which is the floor: each is a sentence some
earlier session already judged to need something.

**One thing here was not asked for.** FR-011 applies the GM's separate 2026-09-12 ruling on the caravan
inn's second story. It is carried in this feature rather than its own because the fix is four lines of a
glyph and a sentence of prose, and a feature of its own would cost a whole gate cycle for that; the
consequence is that this feature's delta touches `l7r/**/*.py` and its route is therefore GATED rather
than the DIRECT route a research-only pass would take. Splitting it back out is the GM's call.

## Who this is for

The reader who clicks a feature on a map, follows "See references" to a research heading, and reads the
paragraph it lands on. That reader cannot tell an assertion the record can back from one it cannot,
unless the page says so. An `(unsourced)` marker in running prose is an honest label but it is not one
of the three forms, it does not appear in any census, and it does not survive into the backlog the
absence notes now constitute.

## Functional requirements

- **FR-001 The inventory is built by an independent reader, not by the author.** Every research page is
  read by a `quote-check` agent, whose documented job includes reporting "per section which assertions
  carry no footnote at all". The session does not decide from its own reading which sentences owe a
  note; it dispatches the check and works the list that comes back. The agent's own reports are kept
  under `reader-reports/`.

- **FR-002 Every entry in the inventory is classified into exactly one of four dispositions**, recorded
  in `research.md` R3 - the inventory proper, R1 being the paragraph census that sizes it - with the page,
  the section and the sentence:
  - `CITE` - it asserts something about the world and a source must be sought.
  - `GROUNDS` - no source is owed, for one of feature 235's six closed-list reasons (measured on our own
    maps; the record's own silence; follows from the definitions; physical necessity; a drawing
    convention; this project's decision).
  - `COVERED` - a footnote already in the same paragraph supports it, and the sentence needs nothing.
  - `NOT AN ASSERTION` - it makes no claim about how a place was built, farmed, planted, governed or
    lived in.

- **FR-003 A `CITE` entry gets a real research pass before any note is written.** The search is
  dispatched to `source-reader` agents, one attempt per host, and the footnote is written from the
  quotes those agents return - never from a search summary, never from the session's own recollection.
  This is constitution Principle XII as it already binds; it is stated here because the failure it
  guards against is exactly what produced this residue.

- **FR-004 Every worked entry ends carrying one of the three footnote forms**, in the shape the
  classifier in `interactive/citations.py` recognizes: a CITATION (key, link, quoted passage), an
  ABSENCE note (`no publicly readable source (searched YYYY-MM-DD: ...)` with the queries), or a GROUNDS
  note (`no source is owed: <reason>` from the closed list). An `(unsourced)` marker in running prose is
  removed when the sentence it marks gets its note, since the note now carries that information in a
  form the census can count.

- **FR-005 A document no client here can read is appended to the GM's download list.** New items go to
  the END of Part 4 of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`, never inserted into the middle,
  each with a clickable markdown link - the direct URL where one is known, and a link to a Google or
  Google Scholar search where the best that can be given is enough to search on. Each entry says what
  rests on it and what blocked the fetch.

- **FR-006 A claim the reading CONTRADICTS is corrected on the page, not quietly dropped.** Feature 232
  found fourteen contradictions in 162 notes; the same rate here would be about a dozen. Each correction
  is recorded in `research.md` with what the page said and what the readable source says.

- **FR-007 The changed entries are checked by the agents that check entries.** `record-format` on every
  changed page (a term a reader would not know, a session note in visible text, the document's own
  history), `quote-check` on every new footnote, and `source-applicability` on every new registry key
  before its numbers reach a map or a rule.

- **FR-008 A modal written from a section whose finding moves is brought back into step.**
  `scripts/_entry_owed.py` names the pairs; each is either read by an `entry-drift` agent and its prose
  rewritten, or covered by one recorded `ENTRY_DRIFT_OK` sweep reason that states no finding moved.

- **FR-009 The pass is worked page by page and lands in batches.** A page's inventory, reading, writing
  and checks complete before the next page's writing begins, so that an interrupted run leaves finished
  pages rather than a half-noted record. `tasks.md` carries one task per page.

- **FR-010 What the pass cannot close is named, not absorbed.** Anything left open at the end - a
  sentence whose source exists only behind a wall, a claim nobody can settle - is listed in the closing
  report with what was searched, exactly as feature 232 named this residue rather than burying it.

- **FR-011 The caravan inn's second story comes down, and the inn is not recorded as a deviation.** The
  GM ruled on 2026-09-12: *"The caravan in does not a deliberate deviation. So if the record draws it as
  two story, then that is simply a mistake. If our attested analog reads it as a single story."* Both
  halves bind. The first is unconditional - the inn's form may not be recorded as a deliberate deviation,
  whatever the story count turns out to be. The second is conditional on the attested analogue, and the
  record already answers that condition with a citation rather than an absence note: `towns.html` fn-25
  quotes the one account read as putting the buildings in the yard uniformly single-story. **So the
  default action is the fix**: the `inn()` glyph in `settlement/civic_grounds/lodging.py` loses its
  upper-story lattice windows, its lower-eave band and the "2-story" in its docstring, and `towns.html`
  states a single-story inn instead of a two-story one qualified by a contradiction. A `source-reader`
  has been asked whether two-story post-station inns are attested in Japan, since the engine's own
  docstring calls the glyph a post-road inn while the analogue read is Manchurian; that reading may
  overturn fn-25 and is reported to the GM if it does, but the fix does not wait on it and is not
  contingent on it. This requirement is the one thing in this feature the GM's request for the research
  pass did not ask for, and it is what makes the delta engine code.

## Success criteria

- **SC-001** (FR-001, FR-002) Every one of the nineteen research pages has been read by a `quote-check`
  agent, and `research.md` R3 accounts for every sentence those agents named, each with one of the four
  dispositions.
- **SC-002** (FR-004) No sentence classified `CITE` or `GROUNDS` in R3 is left without a footnote of the
  matching form; `tests/interactive/test_footnotes.py` is green, and the footnote census tool reports the
  new notes in their classes.
- **SC-003** (FR-003, FR-006) Every new citation carries a verbatim quotation from a page whose URL is in
  the footnote, and every contradiction the reading found is corrected on its page and recorded.
- **SC-004** (FR-005) Every document that could not be read is in Part 4 of `TO-DOWNLOAD.md`, appended at
  the end, with a clickable link; nothing was inserted above an existing Part 4 entry.
- **SC-005** (FR-007, FR-008) `record-format`, `quote-check` and `source-applicability` have run over the
  changed material and their findings are applied; no `entry-drift` pair is left unanswered at push.
- **SC-006** (FR-009) `tasks.md` carries one task per research page, and no page's writing task is ticked
  before that page's own inventory, reading, notes and checks are all done - so an interrupted run leaves
  finished pages rather than a half-noted record.
- **SC-007** (FR-010) The closing report names what is left open, with the searches that failed.
- **SC-008** (FR-011) No `2-story`, `upper-story` or `lower eave` remains in the `inn()` glyph, its
  docstring names a single-story inn, `towns.html` asserts a single-story caravan inn with no
  deviation label, and the reader's verdict on Japanese post-station inns is recorded in `research.md`
  R2 whichever way it came back. Because this requirement puts engine code in the delta: `make done`
  green and the push refused by no guard.

## Decisions recorded

- **D1 The inventory is the agents', not the session's.** The author of a page is not a reliable judge of
  which of its sentences need support - the same reason `settlement-review` exists. This costs a reading
  pass before any research starts, and it is what makes the count trustworthy.
- **D2 `(unsourced)` in running prose is retired where it is met.** It was an honest label and it is
  strictly worse than a grounds note or an absence note: it is invisible to the classifier, invisible to
  the census, and it does not say whether a source was sought. Where a sentence carrying it is worked,
  the marker goes and a note takes its place.
- **D3 The four dispositions include `NOT AN ASSERTION` on purpose.** Feature 235 exists because
  labeling a non-problem as a problem makes the backlog meaningless. A sentence that makes no claim
  about the world is recorded as such and never becomes a note.
- **D4 The caravan inn's fix is carried here rather than in its own feature.** It is four lines of a glyph
  and a sentence of prose; a feature of its own would spend a whole gate cycle on that. The price is that
  this feature's route becomes GATED, which is stated in the Summary and in FR-011 rather than left to be
  discovered. What is NOT deferred is the fix itself: `spec-fidelity` round 1 refused an earlier draft
  that made the redraw wait on a research question the session had thought of, because the GM's condition
  was the attested analogue and the record already answers it. The research still runs; the fix does not
  wait on it.
