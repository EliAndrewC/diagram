# Feature 180 - the references modal lists the QUESTIONS, and the record is written for the reader who clicks

**Status**: FAITHFUL (`spec-fidelity`, round 3 of 5) - cleared for implementation (constitution XVI).
Round 1 returned four drafting items (the link text's count misstated; a lead-in that would have called
every line a "question" on a count that was never checked; FR-012 contradicting FR-006; the registry's
`sources` tuple and the `explanations()` fallback left undefined) and, as an aside, the latent
subdirectory defect now fixed as FR-012a. Round 2 returned one: the corrected FR-008 had swung to
FORBIDDING the GM's own word on a trailing-question-mark metric that filed two of the GM's three quoted
examples as "declarative" - the metric, not the record, produced the finding, and it is withdrawn in
D8. Round 3 returned none.
**Request**: [`request.md`](request.md) - the GM's words verbatim
**Predecessors**: feature 134 (the interactive page and its references modal), 156 (the presumption of
accuracy - a modal announces liberties, not accuracy), 143 (every research entry cites, and every
source carries the URL where it can be read)

## Summary

The interactive map's two modals change what they show a reader, and the project writes down WHO that
reader is and how the record is organized for them.

1. **The explanation modal loses its `Record:` line** - the footer that reads *"Record:
   research/homesteads.md - 'What stood on a farmstead', ..."* (and its variant *"- the research entry
   records no citation yet"*). It is bookkeeping a reader of the map does not need.
2. **The references modal lists the QUESTIONS the research asked**, not the sources. Each is the
   heading of a research section the feature's explanation was written from, and each is a link to that
   section's own anchor on the public GitHub rendering of the research file
   (`https://github.com/EliAndrewC/diagram/blob/main/.claude/skills/diagram/research/<file>.md#<anchor>`).
   The sources move one click further out: the research page is itself cited, and every source there
   carries its URL (feature 143), so a reader who wants the originals still reaches them.
3. **The references modal's close button says where it goes**: *"Return to Farmhouse writeup"* rather
   than *"Close"*, so it cannot be read as closing every modal at once.
4. **The sensibility is documented**: who the audience is (casual RPG enthusiasts curious why a
   settlement looks the way it does), that the record is organized as QUESTIONS a reader might ask from
   the map, and the chain a reader follows - modal -> question -> the well-formatted answer on GitHub ->
   the sources it cites. Written where the next author of a research entry or a modal will meet it.

Only the questions the record already holds are shown. The GM will name the new ones later (*"For now,
you can just limit yourself to the questions that we already have"*); this feature adds none, edits no
research entry and renames no heading.

## Functional requirements

### The explanation modal

- **FR-001** The explanation modal MUST NOT show the `Record:` footer line, in either of its forms (the
  entry pointer, and the *"records no citation yet"* note). The `entry` pointer stays in the class
  registry as the record of what each explanation was written FROM (constitution XII) - it stops being
  RENDERED, it does not stop being recorded.
- **FR-002** The references link MUST read *"See references (N)"*, N being the number of questions
  (FR-004) - today it reads *"See references (N)"* with N the number of cited SOURCES, so the words stay
  and the count changes meaning. It MUST be shown when the entry resolves to at least one question and
  hidden otherwise; today it keys on the entry citing at least one source. Measured (round-1 review):
  of the 52 entries (51 classes and the place card), exactly one - `fallow`, whose entry reads
  *"research/fields.md (no dedicated entry - recorded as silent)"* - resolves to no section, and its
  link is already hidden today because its `sources` is `("not recorded",)`. **No feature loses its
  references link** under the new condition.

### The references modal

- **FR-003** The references modal MUST list, for the open feature, the research sections its class
  entry names - one line per section - and MUST NOT list individual sources (the `key: citation
  [read]` rows it shows today). The sources remain reachable through each question's page.
- **FR-004** A question is one research section matched from the class's `entry` string by the SAME
  rule `sources.research_sources` uses today (a quoted heading matches a section whose heading starts
  with it, or which it starts with, in any `research/*.md` the entry names). The list is in the order the
  entry quotes its headings, deduplicated, so the class author's primary question comes first.
- **FR-005** Each question's text is the section's heading with two kinds of noise removed: the trailing
  bookkeeping parenthetical that carries a date (*"(researched 2026-08-27, feature 133 T41)"*,
  *"(accepted 2026-08-29, feature 152)"*, *"(feature 156, 2026-08-29)"*), and markdown emphasis markers
  (`*`, `` ` ``). Nothing else is rewritten - the heading is the question as the record wrote it.
- **FR-006** Each question links to `RESEARCH_URL + <file> + "#" + <anchor>`, where `RESEARCH_URL` is a
  named constant pinned to `https://github.com/EliAndrewC/diagram/blob/main/.claude/skills/diagram/research/`
  and `<anchor>` follows GitHub's heading-anchor rule: the rendered heading text lowercased, every
  character that is not a letter, a digit, a combining mark, a space, a hyphen or an underscore removed,
  spaces replaced by hyphens, and a heading repeated within one file suffixed `-1`, `-2`, ... in order
  of appearance. A test MUST pin the rule on headings from the live record, including one with a `?`,
  one with a ` - ` (which yields `---`), one with a parenthetical and one with CJK characters.
- **FR-007** The links open in a new tab (`target="_blank"`, `rel="noopener"`), as the source links did,
  so following a question never leaves the map.
- **FR-008** The modal's heading stays *"References - <Name>"*, and it gains one lead-in line above the
  list whose purpose is to tell a casual reader what the lines are and that each links to a written
  answer: *"The questions we asked while working out this feature - each is answered in our research
  notes, with the sources it rests on:"*. "Questions" is the GM's own word for these lines, used
  throughout the request. The lead-in is the one piece of reader-facing text the GM did not ask for,
  and D8 records the decision to have one.
- **FR-009** The close button's text MUST be *"Return to <Name> writeup"*, `<Name>` being the open
  feature's display name capitalized as the explanation's own title is (*"Return to Farmhouse
  writeup"*; for the title placard, the settlement's name). Escape and the button do the same thing they
  do today: close the references modal only, leaving the explanation open.
- **FR-010** The title placard's card (`place.py`) goes through the same renderer and so gets the same
  behavior: its questions come from its own `ENTRY`, and its button names the settlement.

### The data and the code

- **FR-011** The page's embedded JSON carries `questions` (a list of `{text, url}`) per class and drops
  `refs` and `entry`, which nothing on the page reads any more. `sources` (the cited keys) is dropped
  from the page data too; the tests that prove every class's entry cites, and that every cited key is
  registered with a URL, keep reading the record directly through `research_sources` / `registry`.
  **The registry's `FeatureClass.sources` tuple STAYS**, exactly as `entry` does (FR-001): it is part of
  the record of what each class was written from, and `test_classes.py` keeps asserting every class
  carries one. What goes is its one page consumer - the fallback
  `research_sources(fc.entry) or [k for k in fc.sources ...]` in `explanations()` - because a question
  is defined from the entry alone (FR-004) and the fallback has no successor. Blast radius: the single
  entry that resolves to nothing is `fallow` (FR-002), whose fallback was already empty.
- **FR-012** In `sources.py`: `citations()` loses its only consumers (`page.py`, `place.py`, one test
  assertion) and is REMOVED rather than left as dead code owing coverage; `registry()`, `urls_of()`,
  `section_sources()` and `research_sources()` keep their present behavior, because the record tests
  use them to prove every entry cites and every source carries a URL; the question resolver (FR-004)
  and the anchor rule (FR-006) are ADDED to the same module, beside the entry parser they share. The
  removal is a consequence of FR-003, not a widening.
- **FR-012a** **A latent defect the round-1 review noticed is fixed here, per Principle XIV, and
  disclosed as the one code change the GM did not ask for.** `sources._ENTRY_FILE` is
  `research/([a-z-]+\.md)`, which cannot match a file in a subdirectory, so an entry naming
  `research/cities/<x>.md` would resolve to no sources and no questions, silently. No class does that
  today (the 51 entries name only the six top-level files), so nothing on a page changes; the pattern
  MUST accept one directory level, and a test MUST prove an entry naming `research/cities/fabric.md`
  resolves. It is fixed now because this feature builds the URL from that same match, and a town or
  city vocabulary will need it.
- **FR-013** The SVG and the PNG are untouched (feature 134 FR-010); this is a change to the HTML target
  only. No engine module outside `l7r/diagram/interactive/` changes.
- **FR-014** Tests: the page tests assert the JSON shape (FR-011), the anchor rule (FR-006), the noise
  removal (FR-005), the ordering (FR-004) and that every class whose entry quotes a heading resolves to
  at least one question; the browser test asserts the references modal lists links to `RESEARCH_URL`,
  that the button reads *"Return to <Name> writeup"*, and that the `Record:` line is gone.
- **FR-015** The reference hamlet's page is regenerated (`make map GEN=pool/hamlets/inashiro/...`) and
  the result looked at, before the gate. The pool's other pages regenerate at landing (render-sync).

### The documentation

- **FR-016** The approach is written down, in these three places and in this shape:
  - a new `research/CLAUDE.md` - the directory's auto-loading index, which reaches anyone writing or
    changing a research entry - carries the section on WHO the record is for and HOW it is organized for
    them (**amended after the round-3 verdict, see D9**: the draft named `research/README.md`, and
    constitution XVII's guard refused the edit - a README is the GM's to write): the
    audience (casual RPG enthusiasts who want to know a little more about why the settlement is the way
    it is - the crops, the farmhouses), the principle that an entry's heading is a QUESTION a reader
    might ask from the map, the chain modal -> question -> answer on GitHub -> sources, why the sources
    are one click further out (a reader is not to be met with a wall of third-party works), and that
    the GM will be naming new questions to research and record. A new entry's heading is to be written
    as the question the reader would ask.
  - `l7r/diagram/interactive/CLAUDE.md` describes the references modal as it now is (questions, the
    GitHub anchor, the button) and the `sources.py` row says what the module now supplies.
  - the root `CLAUDE.md`'s "WHAT THE RECORD IS FOR" bullet gains the pointer: the reader reaches the
    record by QUESTION, through the references modal, so an entry's heading is written as one.
- **FR-017** Every decision this feature takes that the GM did not spell out is listed under Decisions
  Recorded below, per constitution XII.

### What this feature does not do

- **FR-018** It adds no new questions to the record, edits no research entry, renames no heading and
  touches no `**Sources:**` line. The questions shown are exactly the sections the class entries name
  today.
- **FR-019** It does not change what the explanation modal says about a feature (the what, the why, the
  lead, the caveat, the siblings, the on-this-map note) - only its footer.
- **FR-020** It does not change hover, highlight, zoom, the place card's text or the glossary.

## Decisions Recorded

- **D1 - the links point at `blob/main`, not at a commit.** A reader gets the CURRENT answer, including
  a correction made after their map was rendered. The cost: a renamed heading breaks the anchor on any
  page rendered before the rename. Accepted because `research/README.md` already rules anchors stable
  ("rename a heading only if you also fix its inbound links") and because every pool page is
  re-rendered at each landing by render-sync. The declined alternative - pinning each page to the
  commit that rendered it - would freeze a reader on a superseded answer, the worse failure for a
  record that is meant to improve.
- **D2 - the dated parenthetical is stripped from the question text** (FR-005). *"(researched
  2026-08-27, feature 133 T41)"* is bookkeeping for the project, not part of the question, and the
  audience is a casual reader. The heading itself is untouched in the record, and the anchor is computed
  from the FULL heading, so the link still lands. Rendering decision, class deviation-of-presentation:
  nothing physical behind it.
- **D3 - the link keeps its words and its count, and the count now counts questions.** Today
  `page.js` renders *"See references (3)"* - the number of cited sources. With sources gone from the page
  data the count had to become something or go; it becomes the number of lines the modal will show,
  which is what a count on a link is for. The words stay: the GM spoke of *"the references link"* and
  *"the references modal"* throughout, and renaming either was not asked for. What changes is the
  CONTENT of the modal.
- **D4 - questions are listed in the order the class entry quotes them** (FR-004), not in file order as
  the sources were. The class author put the primary question first when writing the explanation; that
  is the order a reader should meet them in. `research_sources` keeps file order - it feeds a set of
  keys where order does not matter - so the two functions differ deliberately.
- **D5 - the button reads "Return to <Name> writeup"**, the GM's own example with the name capitalized
  as the explanation's title is. "the" is not inserted ("Return to the farmhouse writeup" would be
  smoother English, but the GM gave the form, and a name reads as a title).
- **D6 - `sources` leaves the page data** along with `refs` and `entry`. A reader cannot see it, so it
  would be an invisible payload on every page; the guarantees it used to serve (every class cites; every
  key is registered; every source has a URL) are held by tests over the record itself, which is where
  they belong.
- **D7 - the anchor rule is implemented, not fetched.** GitHub's slugger is reproduced in `sources.py`
  (the rule in FR-006) and pinned by tests on live headings; the page never asks GitHub anything. The
  cost is that a future change to GitHub's rule would silently break anchors; the mitigation is the
  test, which states the expected anchors so a reader comparing against the live site can see the
  rule in one place. **The rule was checked against the live site before this spec was finalized**
  (2026-09-05, a background reader over the rendered GitHub pages): all seven headings tried - a `?`,
  parentheses, an apostrophe, ` - `, CJK characters, markdown emphasis - carry exactly the anchor the
  rule predicts. Untested by that sample: combining marks and non-ASCII punctuation, which no live
  heading uses.
- **D8 - a one-line lead-in stands above the list.** The GM asked for *"a list of those questions"* and
  said nothing about a caption; a caption is a presentational decision the page has to make one way or
  the other, and this is the record of making it. It is kept because a bare list of research headings
  under the word "References" does not tell a casual reader what they are looking at, or that each line
  is a link to a written answer with its sources - which is the whole chain the GM described. It uses
  the GM's word, "questions": many headings in the record carry their answer in the same line (*"May a
  byre stand beside a wellhead? (researched 2026-08-18)"*, *"The outhouse faces the SUN, not away from
  the wind - and 72.7% of them do"*), which is the house form for a research heading, and the caption
  names what they ARE rather than how each is punctuated. An earlier draft of this decision forbade
  the word on a count of trailing question marks; the round-2 review showed the count was an artifact
  of the metric (it filed two of the GM's own three examples as not questions), and it is withdrawn.
  Dropping the lead-in is the declined alternative, and it is one line to drop.
- **D9 - the sensibility lives in `research/CLAUDE.md`, not `research/README.md`** (amended after the
  round-3 FAITHFUL verdict, during implementation). The draft named the README because it is the
  research tree's existing index; `scripts/readme-hooks.sh` refused the edit under constitution XVII
  (*"a README is written by a human for a human; if the GM wants one, the GM writes it"*), with no
  escape hatch, on purpose. The guard's own alternative is the better home: a directory `CLAUDE.md`
  auto-loads for any session working in `research/`, which is exactly the author of a new entry the
  section speaks to, while a README is read by luck. `README.md` is untouched and still holds the entry
  format, the evidence classes and the file table; the new file points at it for those. The GM asked
  for the sensibility to be documented and named no file, so this changes where, not what.
