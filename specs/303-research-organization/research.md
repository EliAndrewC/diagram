# Feature 303 - research (Phase 0)

Every figure here was measured in the clone `diagram-organization` at `8ef670632` (main, 2026-10-01) unless dated
otherwise. The record is `.claude/skills/diagram/research/` (written `research/` below).

## R1 - what the record holds

- 240 research questions in 18 page directories (11 top-level, 7 under `cities/`), 234 drawing questions in 18 under
  `rendering/` (`rendering/cities/` mirroring `cities/`). 1,404 fragment files with notes and originals; the registry
  `research/sources/` is separate and already flat.
- Heading ids are unique across the whole record (0 duplicates; the site build already refuses an id used twice,
  `site.py build_index`), so a heading id can name a site page with no section in its path.
- Question numbers are unique only inside a page directory: 52 numbers recur across the research pages.

## R2 - how research and drawing pair

Each of the 234 drawing pages carries exactly one `<!-- about: <page>.html#<id> -->`. 231 name the research question
of the same part and number. Three name a different number of the same part: `0002` -> `0001`,
`0069` -> `0068`, `0032` -> `0031` - second drawing pages of one research question.
Six research questions have no drawing page: `0012`, `0052`, `0127`, `0067`,
`0133`, `0172`. Plus the three `presentation/` questions, drawing conventions filed as
research (spec FR-008a).

## R3 - the notes' scope

7,276 note definitions; 1,726 keys recur across notes files, so a note key is NOT unique across the record - it is
unique within a page (`notes.merge` refuses a duplicate within one). 19 references in a question name a note defined in
ANOTHER question's notes file of the same page (a note lives beside the question that cites it first, feature 258
stage 3). With one page per question the scope becomes the question's own page; the migration copies each of the 19
notes into the citing question's notes file (refusing if that file already holds the key with a different body).

## R4 - links written inside fragments

Outside HTML comments, the fragments' `href`/`src` values are: 6,367 external URLs; 530 links to another page of the
record (`water.html#id`, `../fields.html#id`); 445 in-page anchors (`#id`, which today may name another question on the
same page); 200 links to the registry (`SOURCES.html#key`, `../SOURCES.html#key`, `../../SOURCES.html#key`); no
`citations/` link. The registry's own fragments hold one internal link (`assets/record.css`). Every non-external form
resolves through the existing `site_links.Index`, so the migration resolves each link with the OLD index and writes the
target's NEW file name.

## R5 - pointers outside the record

Repository-wide (excluding `.git`, the built site): 1,193 fragment-path pointers `research/<page>/NNN-<id>.html`;
1,597 whole-page pointers `research/<page>/`; 484 assembled-page pointers `research/<page>.html[#anchor]`; 24 prose
pointers `research <page> '<heading>'`; 166 `Entry:` lines in the engine. `make fragment-move`
(`scripts/_fragment_move.py`) already rewrites one fragment's pointers; `scripts/_pointer_sweep.py` (feature 301) did a
one-time sweep from page anchors to fragment paths.

## R6 - what depends on the layout

Inventory (sonnet reader, 2026-10-01): 45 scripts and hooks, 14 make targets taking `PAGE=`/`SECTION=` or naming page
directories, 11 engine modules plus about 100 files with comment-only pointers, 28 test files and one fixture tree
(`tests/tooling/fixtures/brief_load/record/`, 12 page directories, 7 briefs), 14 doc and agent files that state the
layout as a rule (`docs/research-record-rules.md` heaviest, 28 passages). Briefs (`specs/*/briefs/*.md`) name
`PAGE=<p> SECTION=<NNN>` or `<page>/NNN` items and ranges; `scripts/_brief_load.py` is their only parser. The glossary
(`interactive/assets/glossary/`) does not depend on page directories.

## R7 - the site today

`record/site.py` hard-codes `GROUPS` (four directory prefixes to four labels) and orders parts by folder name inside a
group. Small pages are `site/<page dir>/<heading id>.html`; maps link them through `sources.SITE_PAGES`
(`research_questions`). Per-page citations pages (`citations/<page>.html`) are assembled for tools
(`footnote_census`, `_quote_verbatim`, `_record_prepass`), not for the site, whose small pages carry their own notes.

## R8 - the tagging pass

240 research questions tagged by four Opus readers in batches of 60 against one vocabulary
(`vocabulary.md` in the scratchpad, carried into `research/tags.json`), each reporting the calls it was torn on; the
session reviewed the whole table and the torn calls (`tags.md`). Drawing pages inherit (spec FR-006).

## R9 - the part openings (spec FR-016)

Filled in by the migration (T05): for each retired part directory, where its `_front.html` reader-facing text went
(the description of the section it introduced) or that it was retired and why.
