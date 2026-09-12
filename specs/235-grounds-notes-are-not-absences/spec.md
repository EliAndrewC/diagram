# Feature 235 - a claim with nothing to find is not an absence

**Status**: ACCEPTED (rewritten against the verified record; the GM reset the review counter on 2026-09-12,
and rounds 1-5 of that count are applied; `spec-fidelity` FAITHFUL at round 5)
**Request**: [`request.md`](request.md), the GM's words verbatim, 2026-09-12.

## The defect

Every footnote in the record is one of two things today: a CITATION (a key, its link and the passage quoted
verbatim) or an ABSENCE note (`no publicly readable source (searched YYYY-MM-DD: ...)`). Feature 195 created
the second so that a claim with nothing behind it would say so instead of standing bare.

It works, and it is being asked to carry a second job it cannot do. Some sentences in the record are not
claims about the world at all. They are numbers measured off this project's own drawings, choices it made,
conventions about how a map is drawn, and statements that the record is silent. Those have no source to
find, will never have one, and are marked with the same words as a claim that badly needs one - so the count
that ought to be a work list is not one.

## What the record actually contains, read rather than described

The eighteen notes an earlier triage proposed for reclassification were read one by one against the pages
([`../232-absence-notes-researched/eighteen-verified.md`](../232-absence-notes-researched/eighteen-verified.md),
corrected to this reading after a review went to the pages and found the first one still too generous).
**The triage was wrong on fourteen of them outright, and three more it called settled are not.** The corrected picture, and the foundation of every factual
clause below:

| | count | notes |
|---|---|---|
| genuinely owes no citation | **1** | `cities/sizing.html` fn-2 |
| arguable, to be argued at its own page | **3** | `religion-and-death.html` fn-49, fn-78; `fields.html` fn-85 |
| genuine open absences, staying in the backlog | **14** | the rest, including `religion-and-death.html` fn-57 and fn-75 |

**This table has now been corrected twice.** The triage proposed eighteen. Reading the pages gave five. A
`spec-fidelity` round that went to the files rather than trusting that reading gave ONE, and its two
strongest findings are the useful ones: `religion-and-death.html` fn-75 is a band the record calls *"a guess
of the same kind"* with *"nothing behind"* it, so FR-003's own second clause forbids it a grounds note; and
fn-57's collar width *"ran"* in the past tense about the real world and its 115 ft was CHOSEN rather than
read off a drawing. A number chosen and then drawn is not a number measured on our own maps, and that
distinction is the one this spec kept missing.

That the problem is a fraction of the size it looked does not make the fix wrong; it makes it smaller. The
labelling defect the GM identified is real and worth a mechanism, and today's record turns out to contain
almost none of it - which is itself the answer to "how many of these are actually problems".

## The four states a footnote may be in, after this feature

| state | what it says | is it a work item? |
|---|---|---|
| CITATION | a key, a link, the passage quoted | no |
| GROUNDS note | `no source is owed: <reason>` | **no** - new in this feature |
| ABSENCE, open | `no publicly readable source (searched DATE: ...)` | **yes - this is the backlog** |
| ABSENCE, settled | the same, plus `settled DATE` and both passes' tools | no - searched to exhaustion; the claim stands as a labeled guess |

## Requirements

**FR-001 The GROUNDS note.** A footnote may say `no source is owed: <reason>`. It means there is nothing to
find. The absence note keeps its present wording and its present meaning, with the one addition FR-004 makes.

**FR-001a A converted note KEEPS its recorded search.** Each of these notes carries a dated search naming
what was read, which feature 232 paid for. On conversion the search text is preserved in an HTML comment beside the reason. **The ground for that is
NOT that a search is session material** - `research/CLAUDE.md` says the opposite, that an absence note's
search is its visible half and only its provenance is a comment, and asserting otherwise would indict every
absence note in the record. The ground is that a grounds note has no absence for the date to qualify, and a
reader owed no source has no use for a search; the text is kept because it is the evidence that the question
was asked before the note left the backlog, and discarding it would throw away what feature 232 paid for.

**FR-002 The reason comes from a closed list, and a note may name more than one.** Free text would make the
new kind a place to put anything inconvenient, hiding real absences instead of separating them. Six reasons,
and the spec is explicit about which the record exemplifies TODAY:

| reason | what it covers | exemplified now? |
|---|---|---|
| `measured on our own maps` | a number read off this project's drawings - not a number chosen and then drawn | **YES** - `cities/sizing.html` fn-2 |
| `the record's own silence` | a sentence whose CONTENT is that no source says this | arguable - `religion-and-death.html` fn-78, if its argument holds |
| `follows from the definitions` | a necessity given what the terms mean | arguable - `fields.html` fn-85 |
| `this project's decision` | a choice we made, naming the ruling and date where a GM ruling exists | no verified instance; `religion-and-death.html` fn-49 may be one, argued at its page |
| `a drawing convention` | how the map draws a thing, as against how the thing was | no instance in the record today |
| `physical necessity` | a necessity of the physical world, independent of period or place | no instance in the record today |

**THE BARRED SET, named so the rule cannot be read two ways.** Three reasons have no verified instance in
the record - `this project's decision`, `a drawing convention` and `physical necessity` - and **none of them
may be used to reclassify an existing note under this feature.** They exist for the FUTURE, which is what
the GM asked about: a vocabulary with no word for "we decided this" would fail the first time a session
needed one. The first time one is used it must be argued in writing against that note's page, and that is a
rule for later work, not a way past this feature's bar.

The two ARGUABLE reasons - `the record's own silence` and `follows from the definitions` - are NOT barred.
They may be used, for `religion-and-death.html` fn-78 and `fields.html` fn-85 respectively, and only on the
written argument FR-006 requires at those pages.

Adding a seventh reason is a change to this spec, not a judgment at writing time.

A note may name SEVERAL reasons where a sentence genuinely rests on several, and every reason it names must
come from the list. Splitting such a note would clutter the reader's page to record a distinction the reader
does not have; the list's protection is unaffected, because what it forbids is an invented reason, not a
second true one.

**FR-003 A GROUNDS note may never carry a claim about the world, and a sentence the record labels a GUESS
about the physical world is never a grounds note.** Anything about how a place was built, farmed, planted,
governed or lived in owes a citation or an absence note, whatever else is true of it. The second clause is
there because it is exactly how the thirteen mistaken rows went wrong: a sentence saying "this rests on
general reading; no source is cited" about how a field was worked is a research question wearing the words
of a disclaimer.

**FR-004 The absence note gains a SETTLED state, so the category is one a claim can leave.** The GM: *"the
number of things in that category should eventually be zero."* Under the rule as it stands that cannot
happen - a claim the record is genuinely silent about keeps an open absence note for ever, so the backlog
has a permanent floor made of work nobody can do. An absence note searched to exhaustion carries `settled
DATE` beside its search, and leaves the backlog. Settling one requires, recorded in the note so a checker
can judge it from the note alone: **two independent passes on different dates, each naming the tools it
used**, the second naming at least one the first did not have. A settled note re-opens on anything that
changes what can be read - a new source, a new tool, the GM supplying a document.

**The bar is a floor, not a licence, and this feature's own evidence says be slow to use it.** Feature 232's
second pass found readable sources for **90 of 162** notes a first pass had marked "no publicly readable
source". Against that base rate a two-pass rule will settle notes a third pass would have resolved, so
settling is never obligatory and a note left open costs nothing but an honest number. The threshold is this
spec's design rather than anything the GM described.

**FR-005 The two counts are produced by a tool, because today nothing counts footnotes at all.** `make
notes-census` counts MAP features and is unrelated; every footnote number quoted in this work was built by
hand. This feature adds the census - open absences, settled absences, grounds notes and citations, per page
and in total - and a test that the numbers it prints are the numbers in the files. Four kinds, matching the
four states above. The open-absence count is the backlog and the only one anybody has to act on.

**FR-006 The eighteen are dispositioned as the PAGES were found to read, not as any summary of them said.**
One - `cities/sizing.html` fn-2 - becomes a grounds note under `measured on our own maps`. Three are ARGUED
at their own pages and become grounds notes only if the argument holds there, in writing: `fields.html`
fn-85 (`follows from the definitions`), `religion-and-death.html` fn-78 (which clause a grounds note would
cover is not settled by the page, since its own comment calls the claim an inference) and fn-49 (whose
section credits a GM ruling - `this project's decision`, which is in FR-002's BARRED SET, so if that is what
it rests on it stays an absence note under this feature and waits; note that the sentence it annotates reads
like fn-2's, so `measured on our own maps` is also a live reading and the argument at the page decides). **The remaining fourteen stay OPEN
absence notes.** Thirteen are barred by FR-003's FIRST clause - each asserts something about how a place was
built or worked while saying no source is cited. `religion-and-death.html` fn-75 is barred by the SECOND: the
record itself calls its band a guess, with "nothing behind" it. Naming which clause carries it should stop
the next reader re-litigating it. This feature returns them to the backlog rather
than removing them from it.

**FR-007 Two sentences addressed to a session are moved into comments, and their footnotes STAY.**
`cities/river-cities.html` carries "Do not 'fix' it."; `cities/defenses.html` carries "which is why it is
really a rule about what may NOT stand there rather than a rule about a road", the record explaining the
form of its own rule to a session, and the reader-facing half of that sentence ("The whole value of it is
that it is unobstructed") stays; feature 209 sends both to HTML comments, and `record-format` missed them.
The footnotes near them - fn-17 and fn-18 - annotate the NEIGHBORING sentences, which are unsourced claims
about the world, so they remain open absence notes. An earlier draft of this spec would have deleted them
with the sentences, removing two genuine research questions from the backlog.

**FR-008 EVERY surface that states what a footnote may be is corrected - there are FOUR, and one is the
constitution.** The GM asked what we can do in the FUTURE, and a vocabulary the checkers and the governing
documents do not know is one the next session will be told is wrong. Two of these four were found only by
review, which is why the list is now argued rather than asserted: the surfaces below are claimed to be
exhaustive, and a round 4 sweep of the record's renderers, the registry tests, the derivation tests, the
format test and the agent files found no fifth.

1. **`.specify/memory/constitution.md`, Principle XII** ("CITE ONLY WHAT CAN BE READ") ends by saying
   `tests/interactive/test_footnotes.py` "holds the two footnote forms". The constitution is the authority
   that `research/CLAUDE.md` operationalizes, so a session reading only it is told the vocabulary has two
   words. It gains the third. **This is an AMENDMENT, not upkeep**: a principle's obligation about what a
   footnote may be is changing, so the constitution's version is bumped - a MINOR, by its own policy, since an existing
   principle is materially expanded - and the GM's words of 2026-09-12 are recorded as the ruling behind it.
2. **`research/CLAUDE.md`** says a footnote is one of exactly two forms and gives CITATION and ABSENCE. The
   grounds note, the closed list, which reasons are exemplified and the settled state land there, and that
   sentence is corrected.
3. **`tests/interactive/test_footnotes.py`** - BOTH the classifier and its consumer. `footnote_form()` gains
   the kind, and `test_every_footnote_resolves_and_every_definition_quotes_a_registered_source`, which skips
   an absence note and otherwise demands a registry-key link and a quotation, must ACCEPT a grounds note
   owing no key, no link and no quotation. Without the second half the first grounds note fails the gate
   whatever the classifier returns, and the requirement would be discovered as a red gate under SC-006.
4. **`.claude/agents/quote-check.md`** tells that agent a footnote with no key and no link that does not read
   `no publicly readable source (searched ...)` is an assertion with no usable citation. A grounds note is
   exactly that shape, so quote-check - which this project runs on every changed entry - would report every
   one as a defect. Its absence-note rule gains the grounds note.

**And a fifth surface this feature may NOT touch.** `research/README.md` says a new entry "cites, or it says
what was searched and not found", which is the same binary in the directory's own reader-facing index. **A
README is the GM's to write (constitution XVII)**, and the authorization the GM gave on 2026-09-12 was for a
specific correction already offered to them, not a standing one. So this feature OFFERS the replacement
sentence in its closing report and does not apply it. If the GM reads that authorization as standing, it is
a one-line change.

**FR-009 The mechanical shape is checked, and the judgment is reviewed.** A test holds the form: every
reason a grounds note names is one of the six; a settled note carries both dates and both passes' tools; a
note is one kind only. The judgment is not mechanical, so `record-format` gains it - for every grounds note
on a changed page, is the reason honest, is FR-003 respected, and where an unexemplified reason is used, is
the written argument there?

## Success criteria

- **SC-001** Each of the eighteen ends in one of two recorded outcomes: reclassified as a grounds note with
  its reason or reasons, or left an OPEN absence note. No footnote is deleted (FR-007). One is expected to
  convert and fourteen to stay; the three argued at their pages fall either way, and the written argument is
  the record of which.
- **SC-002** No grounds note carries a claim about how a place was built, farmed, planted, governed or lived
  in, and none carries a sentence the record labels a guess about the physical world - checked by
  `record-format` over every changed page.
- **SC-003** The census of FR-005 exists and runs, and is run TWICE ON THE SAME TREE, before and after this
  feature's changes, so its counts are judged over this feature's own delta. The global count cannot be used:
  feature 232 is converting absence notes to citations on the same files at the same time.
- **SC-004** The two session-addressed sentences in FR-007 are no longer visible to a reader, and both
  footnotes are still present as open absence notes.
- **SC-004a** All four surfaces in FR-008 know the grounds note: the constitution's Principle XII no longer
  says there are two footnote forms and carries the amendment's version bump; `research/CLAUDE.md` defines
  every form and no longer says there are exactly two; the mechanical classifier returns the new kind AND the
  test that consumes it accepts a grounds note owing no key, link or quotation; and `quote-check` does not
  report a grounds note as a missing citation. `research/README.md`'s replacement sentence is OFFERED in the
  closing report and not applied.
- **SC-004b** Every reason any grounds note names is one of the six in FR-002; no footnote is of two kinds at
  once; and no existing note is reclassified under any reason in FR-002's BARRED SET - `this project's
  decision`, `a drawing convention`, `physical necessity` - under this feature.
- **SC-004c** Every converted note keeps its recorded search in a comment (FR-001a); none is discarded.
- **SC-004d** Every note converted under a reason FR-002 does not mark exemplified carries its written
  argument at its own page, and so does `religion-and-death.html` fn-49 under whichever reason it converts,
  since FR-006 requires the argument there either way - checked by `record-format`.
- **SC-005** Every settled absence note carries two dated passes, each naming the tools it used, the later
  naming at least one the earlier lacked - all judgeable from the note itself.
- **SC-006** `make page-check` green; `make done` green.

## Out of scope

- **Feature 232's research pass** - the first sentence of the GM's message, and its three second-pass
  batches are complete.
- **Re-reading the notes feature 232 converted to citations.**
- **A new label for a GUESS.** The four evidence classes of constitution XII are unchanged; this is about the
  FOOTNOTE's kind.
- **Settling any note.** FR-004 builds the mechanism; this feature ships it with no instance, because settling
  one needs two dated passes and the judgment belongs to that note's own research.
- **Classes B and C of the superseded triage.** They were built by the same unreliable method and have not
  been re-verified; they are feature 232's to re-read, not this feature's to act on.

## Decisions recorded

- **D1 The absence note's wording does not change**, beyond FR-004's `settled` clause.
- **D2 The closed list beats free text**, at the cost of a spec change when a seventh reason appears.
- **D3 The GM's "should eventually be zero" is taken at face value, and FR-004 is what makes it reachable.**
  An earlier draft answered that the sentence was "taken seriously but not literally" and redefined what
  should trend to zero. That was a session narrowing an instruction it found inconvenient;
  `spec-fidelity` caught it. The GM described a property the category ought to have and it did not have it,
  so the category changes.
- **D4 THIS SPEC WAS TWICE BUILT ON DESCRIPTIONS OF THE RECORD RATHER THAN THE RECORD, and that is the same
  failure the feature exists to fix.** Round 3 found two worked examples that did not exist as described;
  round 5 found two more; reading all eighteen found thirteen. An earlier draft added a second footnote form
  on the strength of two of the false ones, and it is gone. The method that produced the error is recorded in
  `eighteen-verified.md`: an extraction heuristic took the sentence nearest each footnote marker, which lands
  wrong whenever a marker sits mid-paragraph, and the classification was made from those extracts without
  opening the pages. **An extraction over HTML is evidence about the extractor.** Every factual clause in this
  spec is now keyed to a note that was read.
