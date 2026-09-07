# Feature 209 - research entries for the reader

**Status**: FAITHFUL (`spec-fidelity`, round 3 of 5; round 1 struck the registry's exclusion - D6 rewritten,
FR-005/FR-006 widened, D1's count; round 2 one word, SC-002 over all sixteen pages) - cleared for implementation
(constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim.
**Predecessors**: feature 134 (the map's glossary: a term in a modal is a hover tooltip); 180 (the record is
written for the reader who reaches it from the map); 194 (the record is hand-authored HTML with hover
footnotes; the `quote-check` agent); 195 (cite only what can be read; the absence note); the 2026-09-07 ruling
that a heading's bookkeeping goes in an HTML comment (`research/CLAUDE.md`, "Who the record is for").

## Summary

The GM read the first entry of `research/homesteads.html` as a reader would and named four things wrong with
it, each *"not only a change to this one specific section, but a general rule for how these research sections
should look"*: a Japanese word with no definition where the map would have given one; bookkeeping written for
a session (`Grounds:`, spec-kit features, task ids) shown to a human; commentary on how the document came to
read as it does (corrections, re-reads, what a sentence used to say); and the terse `Evidence:` field. This
feature (1) gives the record pages the map's glossary tooltips, (2) hides every note-for-a-session in an HTML
comment, (3) removes every reference to the document's own past edits, (4) writes the three as guidelines for
every future entry, (5) applies them to every existing entry, and (6) extends the subagent checks that review
the record so they look for all three.

The pages in scope are all sixteen pages under `research/`: the fifteen research PAGES - `research/*.html`
less `SOURCES.html`, and `research/cities/*.html` - whose `<h2>` sections are the entries the GM's paste is one
of, and the registry `SOURCES.html`, which the map's unread-source links open and a reader reaches from every
citation. The registry has no `Grounds:`/`Evidence:` fields; every other rule holds over it (D6).

## Functional requirements

- **FR-001 The map's tooltips on the record.** The record pages get the SAME glossary the map has: one
  glossary (`l7r/diagram/interactive/glossary.py` stays the single source), every occurrence of a term in a
  page's visible text - headings, prose, footnotes - wrapped in the map's `.gl` span with a dotted underline,
  the definition shown in a box beside the word on hover or focus, placed in viewport coordinates and never
  clipped or off the page (feature 182's ruling). Matching is whole-word and case-insensitive, longest variant
  first, like the map's; nothing inside `<code>`, `<pre>`, `<script>` or `<style>` is touched; the wrap adds no
  text, so a quoted passage keeps its characters. The definitions reach the page as a DERIVED asset,
  `research/assets/glossary.js`, written from `glossary.py` by a make target and committed; a test proves the
  committed file equals the derivation, and every record page (the registry included) loads it before
  `record.js`. The glossary grows with the vocabulary the record uses: every term a casual reader would not
  know that the pages use - the Japanese and Chinese words, the technical terms of farming, water and building -
  gets a definition written from the record's own entries (FR-005 says how the missing ones are found).
  `glossary.py`'s existing test that every term is USED is widened to "used by a modal or by a record page";
  a term used by neither still fails.
- **FR-002 A note for a session is an HTML comment.** The GM: *"anything which is a note for you, which is to
  say a note for Claude code sessions, which are modifying these things, should be hidden in HTML comments."*
  So, in every entry: the `Grounds:` field becomes `<!-- Grounds: ... -->` and the `Evidence:` field
  `<!-- Evidence: ... -->`, both kept - they are what tells a session which rule an entry grounds and how
  strong the finding is - and both invisible; the `Sources:` roster stays visible, because it is the reader's
  list of the works the entry rests on and the map's page and the record tests read it, but any note in it
  addressed to a session (FR-003) goes. Elsewhere in an entry, a spec-kit feature number, a task id, a pointer
  to a spec directory, a test, a make target, a script, an engine identifier (a constant, a function, a knob's
  code name, a file path) is a note for a session: it is moved into an HTML comment beside the sentence it
  annotates, or dropped when the sentence reads whole without it. A key that links to a source is not a note
  for a session and stays. A GM ruling that made a rule, and the alternatives it declined, are the decision the
  record owes its reader (root `CLAUDE.md`, "Record a decision to ACCEPT a limitation") and stay visible, written
  for a reader.
- **FR-003 No history of the document in the document.** The GM: *"I do not see any purpose in recording in
  our research findings references to things which used to be in these documents that were wrong and have since
  been removed ... the commentary about the history of how this research document came to read as it does now is
  pointless. If we ever need to get that information, we can look it up in our version control history."* So
  every reference to a past state of the record or of the maps is removed: what a sentence used to say, a
  correction and its date, a re-read and what it changed, when and how a source was first pointed to, whether it
  was once summary-only, which feature or pass did the work, what "the doc had carried" before. What is kept is
  the information that continues to be useful: the finding, the figures, the quoted evidence, the decision and
  who made it, and the honest label on a claim the record could not support - a GUESS says it is a guess and,
  where it helps the reader, what was searched for and not found; it does not say when the label was applied or
  what the claim was called before. The absence-note footnote form of feature 195 keeps its visible half
  (`no publicly readable source (searched YYYY-MM-DD: what was tried)`) and its history half (*"the passage the
  record carried came from `key`, which is no longer cited"*) becomes an HTML comment naming the registry entry,
  so a session can still find the record of the search.
- **FR-004 The guidelines.** `research/CLAUDE.md` gains a section carrying the GM's words and the three rules
  above as the form of every entry from here: the tooltip, the comment, and the absence of history, each with
  its test in `research/README.md`'s entry format (updated: four fields, two of them comments, the roster's
  form, no `Evidence:` shown). The record tests' file and the `interactive/CLAUDE.md` glossary row say the
  glossary serves both surfaces. The GM's words are the authority; the rules are written so that a session
  writing a new entry can tell a note for itself from a finding for the reader.
- **FR-005 The checks are extended.** Both halves cover all sixteen pages; the registry's verification
  markers live in comments (D6), so no exemption from the visible-text rule is needed for any page. The GM: *"I would like the subagent checks, which review our research,
  to be extended so that they are also checking for all of these things."* Two halves, like feature 194's:
  - a MECHANICAL half at the gate, `tests/interactive/test_record_format.py`, over the visible text of every
    record page (comments stripped): no `Grounds:` or `Evidence:` field; no spec-kit feature number, task id
    or `specs/` pointer; no correction or re-read note (`corrected 20..`, `re-read`, `READ 20..`, `used to
    say`, `used to read`); no `SUMMARY-ONLY` label (the reader's word is GUESS); every page loads
    `glossary.js`; the committed `glossary.js` equals the derivation; every glossary term is used by a modal
    or a record page. A shape the test names cannot come back.
  - a JUDGMENT half, a new check agent `.claude/agents/record-format.md` (Opus, like every check agent - GM
    2026-09-07), the sibling of `quote-check`, run on every new or changed entry before its feature lands and
    over every page in this feature's sweep. Given a page or a section, it reports, per section: (a) VOCABULARY
    that deserves a tooltip - a word a casual reader would not know that the glossary does not define, each with
    a definition drafted from the record's own text, and any word that is defined inline and so needs none;
    (b) NOTES FOR A SESSION still visible - anything the GM's second rule names and anything else written for
    the person changing the record rather than the person reading it, quoted, with the comment or the rewrite it
    proposes; (c) HISTORY of the document still visible - a past state, a correction, a re-read, a provenance
    note, quoted, with what to keep and what to drop. Verification, not judgment about the map: it never decides
    a rule and never edits; the session applies its findings. `research/CLAUDE.md` names it beside `quote-check`
    as what a changed entry owes.
- **FR-006 The sweep.** Every entry of the fifteen pages, and every entry of the registry, is brought under
  FR-001 to FR-003 (the registry under FR-002 and FR-003: its citation-line markers into a comment inside the
  citation paragraph, its `Not cited` dates and feature numbers into comments, its `Citing` instructions and
  its re-sourcing queue - session rules and document history - into comments whole; the entry text a reader
  uses, the work, its URL and what it was used for, stays): the two fields
  commented, the session notes commented or dropped, the history removed, the vocabulary defined. The sweep is
  checked by the agent of FR-005 over every page and its findings resolved before the feature lands; the
  mechanical test is green. The footnotes' quoted passages are not changed, so `quote-check` is not re-run over
  the record (the mechanical footnote tests still hold every footnote's form). The GM's example entry reads, when
  done, as the finding, the figures with their footnotes, the decision on the belt's faces and depth, and the
  Okinawa cross-check - with `yashikirin`, `kainyo` and `sugi` as tooltips and nothing addressed to a session
  visible.
- **FR-007 Verification.** `make page-check` green (the record assets are interactive assets; the synthetic
  browser test of the record's hover covers the glossary box once, on a synthetic page - never a rolled page,
  GM 2026-09-07); `make done` green (the `glossary.py` change and the new tests route the delta GATED); the
  house style holds over every edited page (hyphens, American spellings), with quoted spans left as their
  sources wrote them.

## Success criteria

- **SC-001** Opening `research/homesteads.html#homestead-groves-yashikirin---the-real-scale-and-prevalence` in a
  browser shows the heading's `yashikirin` dotted, its definition on hover; no `Grounds:` or `Evidence:` line;
  no "Corrected 2026-09-07" note; the `Sources:` roster's first item reads as the survey's figures and nothing
  about a pointer's history.
- **SC-002** `grep -c` over the visible text of all sixteen pages (the fifteen research pages and `SOURCES.html`) for `feature [0-9]`, `Grounds:`, `Evidence:`,
  `corrected 20`, `re-read`, `SUMMARY-ONLY` is zero; the same strings inside comments are allowed.
- **SC-003** `record-format` run over every page after the sweep returns no remaining item in any of its three
  classes, or every remaining item is one the session resolved and recorded in `tasks.md`.
- **SC-004** `make page-check` and `make done` green; the tooling that derives `glossary.js` is exercised by
  the test that compares it.

## Decisions Recorded

- **D1 - one glossary, derived to the record, never a second table.** The GM asked for *"the same kind of
  tooltip rules"*; the way to have the same rules is the same glossary. The record pages are static and
  hand-authored, so the definitions reach them as a generated asset, committed like the guard-log reference
  (feature 204) and pinned by a test, rather than by hand-wrapping terms in sixteen pages.
- **D2 - the comment keeps the fields; nothing is deleted from the session's view.** `Grounds:` is what makes a
  stale finding visible (README) and `Evidence:` is the class the four labels are read from; both survive
  as comments, exactly as the GM allowed (*"you can keep that sort of thing in HTML comments"*).
- **D3 - a GM ruling is not history.** "The GM ruled between the two readings: option two" is the decision the
  record must carry (who chose, what was declined); "corrected 2026-09-06, feature 194: the page gives X, not Y"
  is history. The line between them is the GM's own: information *"which continues to be useful"* stays.
- **D4 - the absence note keeps its search and loses its provenance.** "Searched 2026-09-06: mdpi.com 403" tells
  the reader what was tried, which is the honest label on a guess (constitution XII); "the passage came from
  `key`, no longer cited" is how the document got here, and goes to a comment.
- **D5 - a new sibling agent rather than a longer `quote-check`.** `quote-check` fetches pages and compares
  characters; the format check reads one file and judges what a reader sees. One agent per question keeps each
  one's report readable, and `research/CLAUDE.md` binds both to every changed entry, which is how the checks
  are "extended". If the GM would rather have one agent, the procedure sections fold together without loss.
- **D6 - the registry is swept, and its markers move into comments where the classifier still reads them.**
  Round 1 of the spec review struck the first draft's exclusion of `SOURCES.html`: the GM's rule 2 names
  *"references to spec kit features or the history of how things came to be this way"* without scoping it to
  finding entries, and a page that is a record page for the tooltip rule is one for the other two. The one
  machine-read thing on the page - the `READ` / `SUMMARY-ONLY` / `unfetched` markers on a citation line that
  decide whether a key links to its URL or to its entry (feature 190) - is kept, as an HTML comment inside the
  citation paragraph, and the classifier (`tests/interactive/test_sources.py`) reads a comment's text as part
  of the line, so every link target is unchanged. Nothing is exempted from the visible-text rule.
