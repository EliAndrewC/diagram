# Feature 235 - a claim with nothing to find is not an absence

**Status**: DRAFT (spec-fidelity rounds 1-2 applied; awaiting round 3)
**Request**: [`request.md`](request.md), the GM's words verbatim, 2026-09-12.

## The defect

Every footnote in the record is one of two things today: a CITATION (a key, its link and the passage quoted
verbatim) or an ABSENCE note (`no publicly readable source (searched YYYY-MM-DD: ...)`). Feature 195 created
the second so that a claim with nothing behind it would say so instead of standing bare.

It works, and it is being asked to carry a second job it cannot do. Some sentences in the record are not
claims about the world at all. They are choices this project made, conventions about how a map is drawn,
statements that the record is silent, and consequences of what the words mean or of what physics requires.
Those have no source to find, will never have one, and are marked with the same words as a claim that badly
needs one.

The cost is exactly what the GM names: **the count stops being a work list.**

## The four states a footnote may be in, after this feature

| state | what it says | is it a work item? |
|---|---|---|
| CITATION | a key, a link, the passage quoted | no |
| GROUNDS note | `no source is owed: <reason>` | **no** - new in this feature |
| ABSENCE, open | `no publicly readable source (searched DATE: ...)` | **yes - this is the backlog** |
| ABSENCE, settled | `no publicly readable source (searched DATE: ...; settled DATE: ...)` | no - searched to exhaustion, the claim stands as a labeled guess | 

## Requirements

**FR-001 The GROUNDS note.** A footnote may say `no source is owed: <reason>`. It means there is nothing to
find. The absence note keeps its present wording and its present meaning, with the one addition FR-005 makes
to it.

**FR-002 The reason comes from a closed list.** Free text would make the new kind a place to put anything
inconvenient, hiding real absences instead of separating them. The list, and the note it was derived from:

| reason | what it covers | derived from |
|---|---|---|
| `this project's decision` | a choice we made, naming the ruling and date where a GM ruling exists | `towns.html` fn-23, `cities/fabric.html` fn-24 |
| `a drawing convention` | how the map draws a thing, or a consequence of geometry this project itself drew | `archetypes.html` fn-93, `cities/hinterland.html` fn-10 |
| `follows from the definitions` | a necessity given what the terms mean | `fields.html` fn-85, `religion-and-death.html` fn-49 |
| `physical necessity` | a necessity of the physical world, independent of period or place | `cities/fabric.html` fn-29 |
| `the record's own silence` | a sentence whose CONTENT is that no source says this | `cities/fabric.html` fn-22, `religion-and-death.html` fn-50/54/57 |
| `measured on our own maps` | a number read off this project's drawings | `cities/sizing.html` fn-2, `religion-and-death.html` fn-75/78 |

Adding a seventh reason is a change to this spec, not a judgment at writing time. **`setting canon` is
deliberately NOT on this list**: the GM's campaign notes are already a CITATION form, keyed and linked to
their registry entry (feature 195's carve-out, GM 2026-09-07), and no canon citation is converted here.

**FR-003 A GROUNDS note may never carry a claim about the world.** Anything about how a place was built,
farmed, planted, governed or lived in owes a citation or an absence note, whatever else is true of it. A
sentence that mixes the two is SPLIT.

**FR-004 A claim derived from sources cited ELSEWHERE gets a cross-reference citation, not a grounds note,
and the chain must end in a quoted passage.** This is the case FR-003 would otherwise crush: `water.html`
fn-2 states a ratio that is arithmetic on two figures quoted on the same page, and `cities/fabric.html`
fn-18 infers a siting rule from a tower's attested form. Both ARE claims about the world, so neither may be
grounds; neither is unsupported either.

Four conditions, because a footnote that cites footnotes is otherwise a way to launder an unsupported claim
through internal pointers:

1. **Every footnote a cross-reference names is itself a CITATION carrying its own quoted passage.** It may
   not name a grounds note, an absence note, or another cross-reference.
2. **The named footnotes are on the same page as the assertion**, so a reader following the derivation never
   leaves the entry.
3. **The footnote states the STEP**, and the two steps are not the same animal. Arithmetic over quoted
   figures carries its conclusion as far as its inputs go. An INFERENCE does not: the quoted passage supports
   the premise, not the assertion.
4. **An inference says on its face that the conclusion is this project's reasoning over the quoted facts**,
   not something a source asserts. Without that a reader is shown a quotation that does not say what the
   sentence says, which is the one failure constitution XII names.

**FR-005 The absence note gains a SETTLED state, so the category is one a claim can leave.** The GM: *"the
number of things in that category should eventually be zero."* Under the rule as it stands that cannot
happen - a claim the record is genuinely silent about keeps an open absence note for ever, and the backlog
has a permanent floor made of work nobody can do. So an absence note that has been searched to exhaustion
carries `settled DATE` beside its search, and leaves the backlog. Settling one requires, recorded in the
note so that a checker can judge it from the note alone: **two independent passes on different dates, each
naming the tools it used**, the second naming at least one the first did not have.
A settled note is re-opened by anything that changes what can be read - a new source, a new tool, the GM
supplying a document - which is not hypothetical: this feature's own parent re-opened 90 of them that way.

**FR-006 The two counts are produced by a tool and reported, because today nothing counts footnotes at all.**
`make notes-census` counts MAP features and is unrelated; the "162" everyone has been quoting was built by
hand for feature 232. This feature adds the census - open absences, settled absences, grounds notes, cross-reference citations and
source citations, per page and in total - and a test that the numbers it prints are the numbers in the files.
A cross-reference is counted APART from a source citation: it is not a citation in this record's sense (a key,
a link, the passage), and folding the two together would put one label on two different things, which is the
defect this feature exists to end one layer down. The
open-absence count is the backlog and is the only one anybody has to act on.

**FR-007 The eighteen notes named in the triage are reclassified, one at a time, each re-read first.** The
set is enumerated here so that no success criterion depends on a count: `archetypes.html` fn-93;
`cities/defenses.html` fn-18; `cities/fabric.html` fn-18, fn-22, fn-24, fn-29; `cities/hinterland.html`
fn-10; `cities/river-cities.html` fn-17; `cities/sizing.html` fn-2; `fields.html` fn-85;
`religion-and-death.html` fn-49, fn-50, fn-54, fn-57, fn-75, fn-78; `towns.html` fn-23; `water.html` fn-2.
The triage is the proposal, not the authority: a note that turns out to need a source keeps its absence note
and the disagreement is written down.

**FR-008 Two of the eighteen are not notes at all and are fixed as defects.** `cities/river-cities.html`
fn-17 hangs on "Do not 'fix' it." and `cities/defenses.html` fn-18 on a sentence describing this project's
own rule to a session. Both are instructions in the reader's visible text, which feature 209 sends to HTML
comments, and `record-format` did not catch either. Their footnotes go with their sentences.

**FR-008a The record's own definition of a footnote is corrected.** `research/CLAUDE.md` says a footnote is
one of exactly two forms and gives CITATION and ABSENCE. That sentence is what the next session writing an
entry will read, and the GM asked what we can do in the FUTURE - so the grounds note, the closed list of six
reasons, the cross-reference form and the settled state land there, and the "exactly two forms" sentence is
corrected to match.

**FR-009 The mechanical shape is checked, and the judgment is reviewed.** A test holds the form: a grounds
note names one of the six reasons; a settled note carries both dates AND both passes' tools; a cross-reference
names only footnotes that are source citations on its own page; a note is one kind only. The judgment
that a reason is TRUE is not mechanical, so `record-format` gains it - for every grounds note on a changed
page, is the reason honest and is FR-003 respected; and for every cross-reference, does the quoted passage it
rests on actually carry the step the footnote claims?

## Success criteria

- **SC-001** Each of the eighteen notes enumerated in FR-007 ends in exactly one of four recorded outcomes:
  reclassified as a grounds note with its reason; converted to a cross-reference citation under FR-004;
  removed with its sentence under FR-008; or left an absence note with a written argument for why the triage
  was wrong.
- **SC-002** No grounds note carries a claim about how a place was built, farmed, planted, governed or lived
  in - checked by `record-format` over every changed page.
- **SC-003** The census of FR-006 exists, runs, and its open-absence count falls by exactly the number of the
  eighteen that left the open-absence state - reclassified, cross-referenced or removed - with the three
  numbers stated separately so the arithmetic can be checked.
- **SC-003a** Every cross-reference citation names only source citations on its own page, states its step,
  and where the step is an inference says on its face that the conclusion is this project's reasoning.
- **SC-004** The two defects in FR-008 are fixed and no longer visible to a reader.
- **SC-004a** `research/CLAUDE.md` defines all the forms a footnote may take, and no longer says there are
  exactly two.
- **SC-005** Every settled absence note carries two dated passes, each naming the tools it used, the later
  naming at least one the earlier lacked - all judgeable from the note itself.
- **SC-006** `make page-check` green; `make done` green.

## Out of scope

- **Feature 232's research pass** - the first sentence of the GM's message, running as that feature's second
  wave.
- **Re-reading the notes feature 232 converted to citations.**
- **A new label for a GUESS.** The four evidence classes of constitution XII are unchanged; this feature is
  about the FOOTNOTE's kind, not the sentence's evidence class.
- **Settling the seven class-C notes.** FR-005 builds the mechanism; which notes are settled with it is a
  judgment each note's own research owes, and feature 232 is still working several of them.

## Decisions recorded

- **D1 The absence note's wording does not change**, beyond FR-005's added `settled` clause. Most are correct
  as they stand and rewording them would churn the record and break every reader's pattern-match.
- **D2 The closed list beats free text**, at the cost of a spec change when a seventh reason appears. An open
  list is how a category meant to denote problems stops denoting problems, which is the whole defect.
- **D3 The GM's "should eventually be zero" is taken at face value, and FR-005 is what makes it reachable.**
  An earlier draft of this spec answered that the sentence was "taken seriously but not literally" and
  redefined what should trend to zero. That was a session narrowing an instruction it found inconvenient,
  which constitution XVI forbids; `spec-fidelity` caught it. The honest reading is that the GM described a
  property the category ought to have, and the category did not have it, so the category changes.
