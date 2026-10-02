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

Every part directory's `_front.html` carried one reader-facing paragraph, an italic summary of the part (measured by the
migration, `scripts/_record_flatten.py`, 2026-10-01); everything else in it was a session comment about the part's own
history, retired with the part. Each paragraph became the description of the section the part became, in the half it
introduced; none was dropped. Two edits followed, recorded here: the drawing half's descriptions said "the X page" of a
part that no longer exists and now say "the research on X"; the Presentation part's opening - two paragraphs, the second
saying "almost everything on this page is a map drawing convention" - moved to Map conventions' drawing description, since
that section is in the drawing half only, with "this page" read as "this section". The three container sections
(The countryside, Cities, Religion and the dead's subsections) had no part of their own and were given a description of
one sentence each. `_tail.html` (the closing markup and a line linking the part's citations page) and the
`_citations-*.html` shells had no reader-facing text of their own and are retired with the citations pages.

| retired part | its opening went to |
|---|---|
| the archetypes part | section `field-archetypes`, its `description` |
| the buildings part | section `compounds`, its `description` |
| the cities/capitals part | section `capitals`, its `description` |
| the cities/defenses part | section `city-defenses`, its `description` |
| the cities/fabric part | section `urban-fabric`, its `description` |
| the cities/government part | section `government`, its `description` |
| the cities/hinterland part | section `outside-the-walls`, its `description` |
| the cities/river-cities part | section `river-cities`, its `description` |
| the cities/sizing part | section `city-sizing`, its `description` |
| the fields part | section `fields`, its `description` |
| the homesteads part | section `homesteads`, its `description` |
| the presentation part | section `map-conventions`, its `description` |
| the religion-and-death part | section `religion-and-the-dead`, its `description` |
| the rendering/archetypes part | section `field-archetypes`, its `drawing_description` |
| the rendering/buildings part | section `compounds`, its `drawing_description` |
| the rendering/cities/capitals part | section `capitals`, its `drawing_description` |
| the rendering/cities/defenses part | section `city-defenses`, its `drawing_description` |
| the rendering/cities/fabric part | section `urban-fabric`, its `drawing_description` |
| the rendering/cities/government part | section `government`, its `drawing_description` |
| the rendering/cities/hinterland part | section `outside-the-walls`, its `drawing_description` |
| the rendering/cities/river-cities part | section `river-cities`, its `drawing_description` |
| the rendering/cities/sizing part | section `city-sizing`, its `drawing_description` |
| the rendering/fields part | section `fields`, its `drawing_description` |
| the rendering/homesteads part | section `homesteads`, its `drawing_description` |
| the rendering/religion-and-death part | section `religion-and-the-dead`, its `drawing_description` |
| the rendering/settlements part | section `tiers`, its `drawing_description` |
| the rendering/towns part | section `towns`, its `drawing_description` |
| the rendering/urban-features part | section `trades-and-services`, its `drawing_description` |
| the rendering/vegetation part | section `vegetation`, its `drawing_description` |
| the rendering/water part | section `water`, its `drawing_description` |
| the rendering/ways part | section `ways`, its `drawing_description` |
| the settlements part | section `tiers`, its `description` |
| the towns part | section `towns`, its `description` |
| the urban-features part | section `trades-and-services`, its `description` |
| the vegetation part | section `vegetation`, its `description` |
| the water part | section `water`, its `description` |
| the ways part | section `ways`, its `description` |

## R10 - four links that named a whole part

The migration's link resolver (R4) found 4 of the record's 1,175 in-record links naming a whole part rather than a
question - a part is no longer a place to link. Each was pointed, before the move, at the question its text meant, and
these are the only changes of reader-facing words the feature made (SC-003's two "DIFF" lines): the village-boundaries
question's "the religion and death page" became "the question on a village shrine's precinct" (the sacred tree it
spoke of is there); the highways question's "the towns page" became "the questions on a town's inns and its relay
office"; and the smiths-and-farriers drawing page's two links to "the buildings research" now land on the question that
gives the fire gap they cite (the size of a compound and the rank of its buildings), its words unchanged.
