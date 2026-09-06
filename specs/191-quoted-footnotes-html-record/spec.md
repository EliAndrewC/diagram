# Feature 191 - references that QUOTE their sources, checked, and the research record as HTML

**Status**: DRAFT - awaiting `spec-fidelity` (constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim (2026-09-06, three parts)
**Predecessors**: 143 (read what you cite; `SOURCES.md` keys with URLs), 180 (the modal's references are the
research QUESTIONS, linked to GitHub), 190 (every reference is a link)

## Summary

Today a research section ends in a `**Sources:**` line of keys, and the registry entry says what a source was
used for - sometimes with a quote, mostly not. The GM wants the QUOTE to be the citation: *"in our references
section, we quote the passage or passages from the reference which support the assertion that we are making.
There is no point in including a reference if it is not being quoted"* - one footnote per assertion, *"even if this
means multiple footnote links per paragraph or even multiple per sentence"*, a subagent that checks the quote is
verbatim AND supports the assertion AND that every relevant assertion carries a footnote, the whole existing record
backfilled, and the record rendered as HTML with hover footnotes (the ACOUP form), the maps linking to it locally.

## Part 1 - the rule, and the check (FR-001 to FR-005)

- **FR-001 The form of a citation is a FOOTNOTE that quotes.** An assertion in a research entry is followed by a
  footnote reference, `[^n]` (numbered per file), and the footnote at the file's foot carries: the registry key as
  a link (feature 190's rule decides the target), the QUOTED PASSAGE verbatim in the source's language (a gloss in
  English after it when the passage is not English), and, when the quote's bearing is not plain, one clause on
  what it supports. A sentence that makes two assertions from two sources carries two footnotes. Example:
  `Chickens roosted in a coop in Han China[^7], and in Japan the chicken was a timekeeper, not a coop bird[^8].`
  with `[^7]: [`qimin-yaoshu-yangji`](https://zh.wikisource.org/...) - 「雞棲，宜據地為籠，籠內著棧」 (the coop
  is a cage set on the ground with perches inside).` The `**Sources:**` roster stays as the section's key list - the
  modal reads it - and every key on it MUST be quoted by at least one footnote in that section (*"no point in
  including a reference if it is not being quoted"*); a key with nothing to quote leaves the roster.
- **FR-002 A source that could not be read quotes what WAS seen.** A SUMMARY-ONLY entry's footnote quotes the
  search summary it was recorded from, labeled `SUMMARY-ONLY` in the footnote, so the reader sees exactly what the
  claim rests on; a `URL: none` source (the GM's own notes) quotes the note. Nothing is quoted from memory.
- **FR-003 The subagent check.** A new agent, `quote-check` (`.claude/agents/quote-check.md`, Sonnet like
  `source-reader` - verification, not judgment), takes a research file or section and returns, per footnote:
  VERBATIM / DIFFERS (with the page's actual text) / NOT-ON-PAGE for the quote; SUPPORTS / PARTIAL / DOES-NOT-SUPPORT
  for the assertion the footnote is attached to; and, per section, the assertions it finds WITHOUT a footnote (the
  GM: *"every relevant assertion has a footnote link"*). One fetch per host; background; stall-watched like the
  reader. The doctrine: every new or changed research entry is checked by it before its feature lands, and the
  result is recorded in the feature's tasks (the `research: physical` checkbox `source-reader confirmed` becomes
  `quote-check confirmed`).
- **FR-004 The mechanical half is a TEST.** `tests/interactive/test_footnotes.py`: every footnote reference resolves
  to a definition and every definition is referenced; every definition carries a registry key and a quotation
  (quotation marks, 「」 or a `>`-style quote span, at least 12 characters); every key on a section's Sources
  roster is quoted by a footnote in that section; footnote numbers are unique per file. The judgment half
  (verbatim, supports, complete) is FR-003's agent - a test cannot read a page.
- **FR-005 The rule is written where the record is written**: `research/CLAUDE.md` (the form, the check, the
  test), `research/README.md`'s template is the GM's to update (reported), root `CLAUDE.md`'s research bullet, and
  the constitution's Principle XII gains the clause (v2.17.0): a source is cited by QUOTING the passage that
  supports the assertion, and the quote is checked.

## Part 2 - the backfill (FR-006 to FR-008)

- **FR-006 Every existing section is backfilled.** For each of the 183 sections in the 18 files: each assertion
  that rests on a source gets a footnote quoting that source; the quotes come from the page (the `source-reader` /
  `quote-check` agents fetch it), never from memory; a registry entry that already carries the verbatim passage
  (many do - `READ: 「...」`) supplies it directly and the agent confirms it. Scale, measured: 183 sections,
  333 registry entries, 459 keyed citation sites, 202 prose-named ones (feature 190).
- **FR-007 The backfill runs as a batch of background agents, one per file**, each writing footnotes for its file
  and reporting what it could not quote; then `quote-check` runs over every file and its findings are fixed
  (DIFFERS -> the page's text; DOES-NOT-SUPPORT -> a better passage or the assertion re-labeled; a missing
  footnote -> added). The residue - sources that no longer resolve, pages that refuse the fetch - is recorded per
  footnote as FR-002 says, and listed in T-tasks with what was tried.
- **FR-008 What the backfill does NOT change:** no finding's meaning; no label; no rule file. It adds footnotes and
  moves quotes; where a source turns out not to support the assertion it was cited for, that is a CONTRADICTED
  finding and is reported to the GM in the answer, the text left as it is unless the fix is a plain error of
  fact (feature 190's precedent: the year 1697).

## Part 3 - the record as HTML (FR-009 to FR-014)

- **FR-009 Each research file is rendered to an HTML page** with footnotes at the foot and ACOUP-style hover:
  moving the mouse over a footnote link shows the footnote - the source link and the quote - in a tooltip beside
  it, clicking it jumps to the footnote, and the footnote carries a return link. The pages are
  `research/html/<name>.html` (`research/html/cities/<name>.html`), one per source file, with a `SOURCES.html`
  for the registry; section ids equal the anchors the modal already computes (`github_anchor`), so a link that
  worked on GitHub works on the page.
- **FR-010 The record stays AUTHORED in Markdown and the HTML is GENERATED** - the one place this spec departs
  from the request's literal words (*"the markdown on GitHub will no longer exist as it has been replaced with
  HTML"*), put to `spec-fidelity` as a constitution-XVI exception with the reasoning: what the GM asked FOR - hover
  footnotes, many footnote links per paragraph, local links from the maps - is delivered in full by the generated
  pages; what generation preserves is the thing every other artifact here already has: a SOURCE the guards, the
  tests, the parser and the sessions read and edit as text (`sources.py` reads headings and Sources rosters from
  the `.md`; the house-style and SOURCE-block guards act on it; every research edit by every session is a Markdown
  edit), with the rendered form derived, gitignored and regenerated on landing exactly like a map's `.html`
  (`.gitignore`: *"the generated html pages should not be tracked just like the generated svg and png"*).
  Hand-authoring HTML would make every future research edit an HTML edit and the record's diffs markup, for no
  capability the generated page lacks. If the reviewer rules this a carve-out, the files convert (D2).
- **FR-011 The renderer** is `python-markdown` (added to `requirements.in`, re-locked, checked by
  `setup-dev-env.sh`) with its footnotes and tables extensions, wrapped by `l7r/diagram/interactive/researchpage.py`:
  heading ids by `github_anchor`, the footnote hover (inline CSS/JS in the page, no external asset, so a
  `file://` page has everything), the four-label styling the modal uses, a title and a "back to the map" note.
  `make research-html` renders all 18 (+ the registry); the render cache fingerprints the `.md` files and the
  renderer, so a landing regenerates only what changed; `render-sync` calls it in the mirror, which is where the
  GM's laptop reads the files.
- **FR-012 The maps link locally.** `research_questions()` returns a path RELATIVE to the map's own page -
  `../../../research/html/homesteads.md.html#anchor` from `pool/<tier>/<name>/<name>.html` - and the references
  modal opens it in a new tab as before. `RESEARCH_URL` (GitHub) is retired; the class entries' `entry` strings
  are unchanged (they name `research/<file>.md`, which the resolver maps to the page).
- **FR-013 Tests**: the renderer (ids equal `github_anchor` for every heading in every file; every footnote
  rendered with its hover data; a SOURCE block rendered verbatim; the tables); the links (every question URL a
  map emits resolves to an existing page and an existing id); the `page` stamp area gains the renderer's assets;
  100% coverage as everything else. The browser test opens one research page and hovers one footnote.
- **FR-014 Documentation**: `interactive/CLAUDE.md` (the page chain now ends at a local page),
  `research/CLAUDE.md` (the HTML is generated - edit the `.md`), `dev/cache.md` (the research fingerprint).

## Decisions Recorded

- **D1 - footnotes, not inline quotes.** The GM named footnotes and the ACOUP hover; a quote inline after every
  assertion would double the record's length on the page and bury the argument.
- **D2 - Markdown source, generated HTML** (FR-010) - held for `spec-fidelity`'s ruling under XVI.
- **D3 - the Sources roster stays and is bound to the footnotes.** The modal reads keys per section from it; the
  footnotes are where the quotes live; FR-004 binds the two (every roster key quoted). Declined: deriving the
  roster from the footnotes (the modal's parser and 190's test both read the roster; two consumers would change
  for nothing the reader sees).
- **D4 - numbering per FILE** (`[^1]` ...), the Markdown footnote convention, so a footnote is the same number in
  the source and on the page and GitHub's renderer shows the same footnotes while the `.md` still renders there.
- **D5 - the backfill is per file, in parallel, and checked by a second agent.** The writer agent and the checker
  are different runs so the check is independent (constitution I's author-is-not-reviewer rule).
