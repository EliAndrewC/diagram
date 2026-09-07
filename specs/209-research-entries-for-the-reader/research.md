# Research - 209 research entries for the reader

Nothing physical: every decision here is about the FORM of the record (`research: rendering`).

## R1 - what the record carried, before (census 2026-09-07, main at 4a8e86ff)

Fifteen research pages, 174 `<h2>` sections. Visible to a reader: 287 `Grounds:`/`Evidence:` fields (two of
them merged into a neighbor's paragraph); 20 correction notes of the form `(corrected 2026-09-06, feature 194: ...)`
plus the GM's example `(Corrected 2026-09-07. ...)`; 34 `feature NNN` mentions in bodies (capitals 16, homesteads 16,
buildings 15, vegetation 15); 49 task ids (`T57`), 43 of them in vegetation and homesteads; 61 `SUMMARY-ONLY`
labels; 52 absence footnotes carrying the "no longer cited" provenance tail; roster parentheticals with `READ`
dates, re-reads and "the pointer was summary-only until the GM asked"; and, in the bodies, about 560 `<code>` spans
of which roughly a third are engine identifiers rather than source keys (water: `MIN_CHANNEL_PX`, `aze_w`,
`build_comb`, `supply_bank_clearance`). Vocabulary: about 90 romanized Japanese or Chinese words and units in
`<em>` or plain, of which the map's glossary defined 27 (e.g. `yashikirin`, `tsubo`) and the record defined none.

## R2 - how the sweep was run

The two fields were commented by one script (`specs/209/.../fields_to_comments.py` in the session's scratchpad,
reproduced in tasks T03); the judgment half - a note for a session, a piece of history, a term - by seven
editing agents (one per page or page group, on the session's own model; editors, not checks) under a written
rulebook that quoted the GM's three rules, listed the shapes, named what NEVER changes (headings, ids, every
footnote reference and its position, every quoted passage, house style outside quotes) and ended with the four
test files each editor had to run green. Then the `record-format` check (Opus) over every page, its items resolved
by the session. The mechanical test (`FORBIDDEN_VISIBLE`) is the floor under both.

## R3 - the glossary boundary in JavaScript

`page.js` matches with `\b`, which is ASCII-only in JavaScript: `\bōkajiba\b` never matches at the macron.
`record.js` uses `(?<![\p{L}\p{N}])...(?![\p{L}\p{N}])` with the `u` flag instead - the same whole-word rule,
Unicode-aware - checked on `yashikirin`, `ōkajiba`, `Yashikirin`, `head race` against `headland` (no match) in
Node before it shipped. `page.js` is untouched: no modal term carries a macron, and the GM's rule for assets is
that an edit owes `make page-check`, which this feature runs anyway.

## R4 - one box for two hovers

The footnote hover already owned a positioned box (`#fntip`, feature 194). The glossary definition shows in the
same box by `textContent`, placed by the same `place()`; the footnote path sets `innerHTML` from the note. One
element, one placement rule, one Escape handler; the map's `#tip` stays the map's (a different page, a different
stylesheet).

## R5 - the registry's markers (D6, after review round 1)

`SOURCES.html`'s citation lines carried `READ YYYY-MM-DD`, `SUMMARY-ONLY`, `unfetched`, feature and task
numbers, and 26 entries opened with `READ 2026-09-06 at <url> (feature 195):` - the public page the passage was
read on, which the classifier picks as the FIRST URL on the line. All of it moved into one comment per citation
paragraph (the read-at comment FIRST, so the first URL is still the read-at one); the classifier's `_text` now
folds a comment's text back into the line, and every one of the 400+ link targets the test checks is unchanged.
The `Citing` section (rules for sessions) and the re-sourcing queue (document history) are comments whole; the 31
`Not cited (2026-09-06, feature 195)` lines keep `Not cited` visible with the date and feature in a comment. A
first pass split a citation's parenthetical on `;` and broke every `&amp;` in a URL - caught by the classifier
test, redone with an entity-safe split.

## R6 - a parallel sweep must not run tests per agent

Seven editing agents each ran four test files (pytest at eight workers) at the end of their work, beside another
session's gate. The container's pids cgroup (2,048, threads included) was hit 447 times, `/bin/sh` could not
fork the prompt hooks, and Claude Code read the shell's exit 2 as a BLOCK of the GM's prompt and of one agent's
completion notice. The launcher sets no `--pids-limit` (the runtime's default); raised with the GM. In this
repository: an editing agent reports, and the session runs the tests once.
