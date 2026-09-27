# research/ - the historical record: the rules

This file auto-loads into every session that reads a research file, on every turn, so it carries the RULES and
nothing else. Why each is the rule - the GM's words, the incidents, the measurements - is in
[`docs/research-record-rules.md`](../../../../docs/research-record-rules.md), under the same headings; read it
before arguing with a rule. The entry format and the evidence classes are in [`README.md`](README.md).

## Where things are (feature 258)

| what you want | where it is |
|---|---|
| a source's registry entry | `research/sources/010-works-cited/NNNN-<key>.html` |
| a question | `research/<page>/NNN-<heading id>.html` |
| that question's footnotes | `research/<page>/NNN-<heading id>.notes.html`, beside it |
| a `cities/` page | `research/cities/<page>/...`, the same shape one level down |
| the page a reader opens | `research/<page>.html` - ASSEMBLED, never hand-edited |
| a glossary term | `l7r/diagram/interactive/assets/glossary/NNNN-<term>.json`, one file per term (feature 259) |

Find one with a glob on the key (`ls research/sources/*/*fei-1939*`) or a grep over the page's directory - never
`ls research/sources/` bare (920 entries), never open an assembled page to edit it (the guard re-aims the Edit).
`research/assets/glossary-variants.txt` maps a word to the term that owns it; grep it, never read it whole.

**Editing.** Edit the fragment, then `make record` (and `make citations` for notes, `make glossary` for a term)
in `.claude/skills/diagram`. **A question**: a free prefix between its neighbors (they count by ten), the file
opening with its `<h2 id="...">`. **A footnote**: no number anywhere - `<sup class="fn" data-note="<key>"></sup>`
in the prose, `<li data-note="<key>">...</li>` in the `.notes.html`; repeats of one work are `key`, `key-2`, ...
**A term**: a new file with a free prefix; the prefix order decides which term wins a shared variant. The
assembled `assets/glossary.json` and `research/assets/glossary.js` are written by `make glossary` and never hand-edited.

**Checking** (feature 250). `make check-bundle PAGE=<p> SECTION=<q>` (or `KEY=<k>`; `KIND=<class>` for
`entry-drift`; `NOTES=<key,key>` to re-check only those) copies what ONE check reads out of the repository,
inline in one `MANIFEST.md`; dispatch the check naming that MANIFEST and nothing under `/diagram` - reading a
file here would attach ~28,000 tokens of CLAUDE.md files to the agent, and `check-bundle-hooks.sh` refuses the
dispatch. A check replies with its counts first, then only what to act on. `make notes PAGE= SECTION= KEYS=`
prints a few notes and the paragraphs carrying them. **A page is worked in fresh sessions** (`make page-session`
with briefs: write, then check-and-apply in groups of two questions), and a report's findings are applied in
ONE turn - every turn re-reads the whole context.

**A cheaper check is proved** by every candidate the prepass raised being ruled on (feature 260) - not by "the
same findings"; a TIER downgrade is proved by seeded runs on known findings, three a leg.

## A question has a size (feature 250 D14, GM 2026-09-26)

A question with its notes stays under 20,000 bytes (`scripts/check-question-size.py`; `make quick` fails on one a
change touched; `make question-sizes` lists all). One over it is split along its topics: a finding stays with the
decision it drove; each part is its own question with its heading, `Sources:` line and notes; the joins POINT at each
other, never restate each other's evidence. A split that would strip a finding of what it needs is not made - it is
raised instead.

## Who the record is for (GM 2026-09-05, feature 180)

The reader is a casual RPG enthusiast at the map, not the next session. They go map -> modal -> "See
references" (the QUESTIONS we asked) -> the answer on the research page -> the sources. So:

- **A heading is the question a reader would ask from the map**, the answer allowed in the same line. The
  bookkeeping (date, feature, task) is an HTML comment on the next line, never in the heading.
- **An anchor is stable**: a renamed heading owes its inbound links - the class entries' `Entry:` tags
  (`scripts/check-entry-headings.py` fails the gate on one that resolves to nothing). A section deliberately not
  written is `research/<file>.html (no dedicated entry - recorded as silent)`.
- A class's explanation names the entries it was written from; that pointer is all that puts a question on a
  modal. New questions reach a modal only when the GM asks for them.

## Four labels (GM 2026-09-05, feature 183)

A finding and the modal written from it carry one of four labels: **accurate**, **deviation** (the setting
differs from the history it is based on), **convention** (a glyph drawn at another size or color so the map
reads), **guess**. A convention's modal note says so in the GM's form and ends with the real size or color, or
says it was searched for and not found. The word is the same in the entry, the rule, the code comment and the
map's notes.

## Every reference is a link (GM 2026-09-06, feature 190)

A key is never bare. A document we READ links to the first URL on its registry citation line; one we did not
read (`SUMMARY-ONLY`, `URL: none`, `unfetched` without `READ`) links to its registry entry. The key is the link
text. A work named in prose, or by its author's surname at first mention in a section, is linked the same way;
a read document with no entry gets one first (after searching the registry by URL, percent-decoded, and by the
whole entry), and nothing links to a URL nobody fetched. A new entry records the URL and its READ date. A `Pointers, not read:` item with no entry, a page named only as
silent or unreadable, and an unregistered summary-only or withdrawn item stay plain; a REGISTERED name is linked
whatever label surrounds it.
`tests/interactive/test_sources.py` holds it.

## A reference QUOTES what it rests on (GM 2026-09-06, feature 194)

A footnote per assertion - several a sentence when it asserts several things, two on a sentence resting on two
sources - and every note quotes the
passage it rests on, VERBATIM including the source's own spelling and dashes (the house-style guard exempts
quoted spans). A foreign passage is quoted in English translation, marked: `「English」 (translated from the
Japanese by this project; original: 「原文」)` - the translation follows house style, the original follows the note.
The note names the language and the translator; a source's own English needs no note; the original is the
checker's anchor, never a second quote. The same form holds in body prose and in a `SOURCES.html` entry. The section's
`<p><strong>Sources:</strong> ...</p>` roster stays, every key on it is quoted by a footnote in that section, and a key
with nothing to quote leaves the roster. Nothing is quoted from memory.

## A citation links to a page where its quote can be READ - or it is not a citation (GM 2026-09-06, feature 195)

A note is one of THREE forms:

- **CITATION**: `<a href="https://..."><code>key</code></a> - 「passage」 (gloss)` - the link a public page on which
  the passage can be read: the paper's public PDF, not its abstract; the full-text view, not a library landing page;
  the original-language page, not an English rendering that is on no page. Never a paywall, a login wall or a
  search summary.
- **ABSENCE**: `no publicly readable source (searched YYYY-MM-DD: what was tried)` - no key, no URL; the
  assertion stands, honestly labeled; the registry entry stays, marked *Not cited*. It may carry `settled DATE`
  only after two independent passes on different dates, the second using a tool the first lacked, and it re-opens
  on anything that changes what can be read. Settling is never obligatory.
- **GROUNDS**: `no source is owed: <reason>` from a CLOSED list - `measured on our own maps`, `the record's own
  silence`, `follows from the definitions`, `physical necessity`, `a drawing convention`, `this project's
  decision`. NEVER for a claim about how a place was built, farmed, planted, governed or lived in, nor for a
  labeled GUESS about the physical world - those owe a citation or an absence note. A note may name more than one
  reason; using one of the four not yet exemplified on an existing note takes a written argument at that note's page. A note converted
  from an absence note keeps its search in an HTML comment.

The one exception, by the GM's ruling: the GM's own campaign notes are canon and keep their registry link. A page
the container cannot fetch is not thereby unreadable - if the GM can open it, anyone can; a source only the GM
can fetch is downloaded by them to `/host-l7r-repo/academic-sources/` - the session reads the copy, the footnote
links the PUBLIC page and says the copy was read, and the quote-check runs against the copy; a paywalled text with a
public abstract is cited for the abstract's words only; what a read copy does NOT say is written down where the
claim stands, and the rest labeled GUESS. A source for the GM to fetch goes at the END of
`/host-l7r-repo/academic-sources/TO-DOWNLOAD.md`, in Markdown, one entry per work:
a heading naming it, a link to where the session believes it lives, a Google-search link that uniquely finds it,
what rests on it, and what blocked the fetch - BOTH links, always.

`tests/interactive/test_footnotes.py` holds the mechanical half. The **`quote-check`** agent holds the rest -
per note VERBATIM / SUPPORTS, per section the assertions with no footnote - after `make quote-verbatim`, on
every new or changed entry, its verdicts recorded in the task (`quote-check confirmed`).

## Written for the reader (GM 2026-09-07, feature 209)

1. **A term the reader would not know is a glossary tooltip** - one glossary for the map and the record, each
   definition written from the record's own text; nothing is wrapped by hand. A term nothing uses fails the gate.
2. **A note for a session is an HTML comment**: the `Grounds:` and `Evidence:` fields, a feature, a task, a spec,
   a test, a make target, an engine identifier, a fetch verdict. Visible: the `Sources:` roster (each key's
   parenthetical says what the work contributed, never when or how it was read), a source key's link, a GM ruling and the alternatives it declined, the honest label on a claim (a GUESS, a dated search).
3. **No history of the document in the document**: no "used to say", no correction dates, no "re-sourced by".
   A changed finding is REWRITTEN; git holds the old wording. An absence note's provenance ("the passage came from
   `key`") is an HTML comment inside its `<li>`.

`tests/interactive/test_record_format.py` holds the mechanical half; the **`record-format`** agent (after
`make record-prepass`) the rest - VOCABULARY, SESSION NOTE, HISTORY - beside `quote-check` on every new or
changed entry - two agents, dispatched in the same turn (spec 209 D5). The registry is not under rules 2 and 3.

## The notes live on a CITATIONS PAGE; every cited work says what it is (GM 2026-09-07, feature 211)

- `research/citations/<name>.html` holds every note of `<name>.html` once; the research page loads the DERIVED
  `citations/<name>.js` for the hover (`make citations`; the gate fails a stale one).
- **A registry entry explains its work once**: after the citation line, `<p><em>What it is:</em> ...</p>` and
  `<p><em>Why it applies, and its limits:</em> ...</p>`, each one to three sentences, honest about date, place
  and method. A cited key without both fails the gate; the works section of a citations page is derived from them.
- **A source is judged before it is used**: the **`source-applicability`** agent on every new or changed write-up,
  and BEFORE a source's numbers, claims or details reach a map or a rule (a physical task's fifth box). A
  NOT-APPLICABLE source is recorded and listed for the GM, and the assertions resting on it keep their label until the
  GM rules.

## The record IS HTML (feature 194)

The record's files are hand-authored `research/<name>.html` (and `cities/`, `SOURCES.html`, `citations/`); a page's
`<head>` links `assets/record.css`, `assets/record.js` and, on a research page, its `citations/<name>.js`; section ids
are the anchors. `README.md` and this file stay Markdown. The page mechanics are in
[`../l7r/diagram/interactive/CLAUDE.md`](../l7r/diagram/interactive/CLAUDE.md).

## The record is the ONE home per topic (GM 2026-09-12, feature 229)

Per question a page holds the finding, the decision it drove (the ruling, its date and words, the alternatives
declined), and - for a rule no generator yet encodes - the **specification**, `<p class="spec"><strong>The rule
the map follows:</strong> ...</p>`, in real feet at the tier's scale (the pixel figure in a comment beside it), naming no engine identifier or check in
its visible text, and - where it rests on no finding - saying which it is: a convention, a calibration against the
drawn exhibits, or a guess; it is retired once a generator encodes the rule with its reasoning. A rule the engine
encodes with its reasoning is not written twice; a reason its code comment lacks goes on the page, and the comment
points at the anchor. Nothing names a retired
`settlements/*.md` rule file (`tests/interactive/test_record.py`).

## When a section a modal was written FROM moves (GM 2026-09-12, feature 234)

A modal IS its `Kind` class's docstring (`interactive/classes/`), written from the section its `Entry:` names.
`scripts/_entry_owed.py` names every class whose section's BODY changed while its prose did not; the push refuses
until each pair is answered - an `entry-drift` check and a rewrite of what it calls DRIFTED, or one recorded
`ENTRY_DRIFT_OK="<what moved, and why no modal is now wrong>"`. `record-format` and `quote-check` are NOT this
check: neither opens a modal.
