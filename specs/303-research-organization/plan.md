# Implementation Plan: the record organized by tags

**Branch**: none (main, clone `diagram-organization`) | **Date**: 2026-10-01 | **Spec**: [spec.md](spec.md)
**Input**: the accepted spec (FAITHFUL at round 3) and [request.md](request.md)

## Summary

The record's topic directories go; every question becomes one stem in `research/questions/`, tagged from a vocabulary
in `research/tags.json`, and `research/contents.json` declares the sections, their order and the tag rule each takes.
The site builder is rewritten around questions and sections instead of pages; every link inside the record, every
pointer in the repository, every tool that took `PAGE=` and every doc describing the layout move to the new form in one
landing. The migration is a one-time script that resolves every old link with the OLD link index (research R4) and
writes a mapping file the pointer check reads, so nothing is rewritten by guesswork.

## Technical Context

**Language**: Python 3.12 (engine `l7r/`, tools `scripts/`), bash hooks, JSON data, HTML fragments.
**Testing**: pytest through `make quick` / `make done`; hooks through `make hooks-test`; 100% coverage over the engine.
**Target**: `make record` (site build), `make record CHECK=1` (at the push), the map pages' modal links.
**Constraints**: no file past 1,000 raw lines; nothing in the engine reads the built site; two builds byte-identical.
**Scale**: research R1 (474 question pages, 1,404 fragment files) and R5 (the pointers).

## Performance bookends

N/A for the generator: no map's geometry changes (constitution VI applies to generator changes). The record build is
timed before and after (`make record`) and stated in the closing notes; a slowdown is diagnosed, not assumed.

## Constitution Check

- I, II: N/A - no UI in this repository beyond the record site, whose look is unchanged (same stylesheets, same shell).
- III, IV, V, VII, VIII, IX: N/A - no pool content, no SOURCE block moved or edited (the sweep skips SOURCE blocks and
  `request.md` files), no in-world content, no setting detail.
- VI: PASS - every task names its verification; the closing phase runs `make record CHECK=1`, `make hooks-test`,
  `make done`, and checks every pool map's research links (SC-009).
- X: PASS - ruff, format, pyrefly, red-green tests for each new behavior (the refusals of FR-007/FR-010 are written as
  failing tests first), 100% coverage; `site.py` stays under 1,000 lines by splitting into `site.py` (the build) and
  `site_pages.py` (sections, tags, navigation), and the new `questions.py` / `contents.py` are small modules.
- XII: N/A for the world - no rendering decision is made; the decisions are organizational and are in the spec's
  Decisions Recorded. The record's CONTENT is unchanged (SC-003 holds it mechanically).
- XIII: PASS - baseline `make done` on unmodified main in a detached worktree (`/tmp/base303`, commit `8ef670632`),
  its result recorded in the closing notes; zero new failures at landing.
- XIV: defects found on the way are fixed in this feature.
- XVI: the plan's decisions below are reviewed by `spec-fidelity` (MODE 4) before any task is ticked.

## Decisions

**D1 - The layout.**

```
research/
  questions/NNNN-<slug>.html                 the research page
  questions/NNNN-<slug>.notes.html           its notes          (.originals.html: its originals)
  questions/NNNN-<slug>.drawing.html         how our maps draw it
  questions/NNNN-<slug>.drawing.notes.html   its notes          (.drawing.originals.html)
  sources/                                   the registry, unchanged
  tags.json  contents.json  confusables.json
  moved-303.json                             old path -> new path, migration data only (never a redirect)
  assets/  site/ (built, gitignored)  CLAUDE.md  README.md  STYLE.md
```

`<slug>` is the research page's heading id; for a drawing-only stem, the drawing page's heading id. `NNNN` is four
digits, allocated once at migration in the order the new table of contents reads (section order, then level, then the
old page order, then the old prefix), so the first numbers fall where a reader starts; a later question takes the next
free number from `make reserve KIND=question`. The number is identity; a later regrouping never renumbers.

**D2 - The markers.** A research page (or drawing-only page) states its tags on the line after its heading:
`<!-- tags: subject=homesteads,buildings; setting=countryside; level=detail -->`. A second drawing page of a question
(R2's three) is its own stem holding only a `.drawing.html`, and says whom it is about on the line after its heading:
`<!-- about: 0412-clustered-and-scattered-villages-shuson-sanson -->`; it inherits that stem's tags. A paired drawing
page needs no `about:` (the stem pairs it), so the 231 paired declarations are removed. The three Presentation
questions become drawing-only stems (`.drawing.html`, own tags, primary subject `map-conventions`).

**D3 - The notes' scope.** A page's references resolve only in its own notes file. The migration copies each of the
19 cross-question notes (R3) into the citing page's notes file. The single page numbers its notes once across the
record by (page, key).

**D4 - Links inside the record.** Every link in a fragment or notes file is written relative to `questions/`:
`NNNN-<slug>.html[#id]`, `NNNN-<slug>.drawing.html[#id]`, `../SOURCES.html#<key>` for the registry, `#id` only for an id
on the same page. The build resolves them against an index of every page's ids and refuses one that lands nowhere,
naming the file. The migration rewrites R4's links by resolving each with the old index.

**D5 - The vocabulary and the contents.** `tags.json`: `{"subject": {id: {name, description}}, "setting": {...},
"level": [ordered ids with names]}`. `contents.json`: an ordered tree of sections `{id, title, description, takes,
sections}`; `takes` is a list of clauses, each an object whose keys (`primary`, `subject`, `setting`, `level`) must all
match (values may be a list = any of). Home = first section in depth-first order whose `takes` matches. Initial
contents: FR-013, every leaf taking `{"primary": <its subject>}`. Map conventions sits last before Sources.

**D6 - The site.** `site/index.html` (both halves, sections nested); `site/findings/<section>.html` and
`site/drawing/<section>.html` (a section's page in each half: description, subsections, its questions in order - the
research half's directory is not `research/`, because a path `research/<x>.html` is what the pointer check refuses as a
retired built page);
`site/q/<heading id>.html` (every question page of both halves - flat, so a regrouping moves no URL);
`site/tags/<facet>-<tag>.html`; `site/sources/...` (unchanged); `all.html`; `nav.js`. Each question page shows its tags
(linked to their pages), its notes numbered from 1, its works, and the research/drawing cross-link. Maps link
`site/q/<heading id>.html` (`sources.SITE_PAGES` + `q/`).

**D7 - Part openings.** Each `_front.html`'s reader-facing intro moves into the description of the section it
introduced (by the part -> section mapping of D8); session comments in it are dropped (they describe the part's
history); `_tail.html` and `_citations-*.html` are deleted. Per-part citations pages are retired: the site never served
them, and the three tools that read them (R7) read the per-question notes instead. `research.md` (R9, spec FR-016)
lists each opening and where its text went, or that it was retired and why.

**D8 - Pointers.** The sweep rewrites, repository-wide: a fragment path `research/<page>/NNN-<id>.html` (and its
`.notes`/`.originals`) to `research/questions/NNNN-<slug>[.drawing][.notes|.originals].html`; an assembled-page pointer
`research/<page>.html#<anchor>` to the stem holding the anchor (with `#anchor` kept when it is not the heading); a
whole-page pointer `research/<page>/` or `research/<page>.html` to the section the part became,
`research/contents.json#<section id>`; a prose pointer `research <page> '<heading>'` to the stem; and an old number
`<page> NNN` or `<page>/NNN` naming an existing question (a page name and its three-digit number) to `NNNN` (three digits after a page
name; every number-form rewrite is listed for review in `migration.md`, because prose can put a page name before a
number that is not a question). The pointer check (`check-research-pointers.py`) validates the new forms (a stem file
exists; a section id exists in `contents.json`) and refuses every old form whose old path or (page, number) is in
`moved-303.json`, naming the new pointer from it. Exempt: `specs/*/request.md`, SOURCE blocks, `moved-303.json`, and
`specs/303-research-organization/migration.md`, which holds only the generated old-to-new mapping. Everything else in this
feature's own directory is swept and checked like any landed spec. A range in a landed brief (a page name and a span of numbers) is
rewritten to the new numbers of the questions it covered; a range covering no question names no research file and is
left as written - it passes the check without an escape, because the check refuses only a (page, number) that IS in
the mapping, and neither end of such a range is.

**D8a - What the sweep and the check met on the way (implementation, 2026-10-01).** (1) A pointer of a retired form was
also written as a tool's argument, `PAGE=<page> SECTION=<NNN>` and a bare `PAGE=<page>`; these are rewritten to `Q=<NNNN>`
and `IN=<section>` like any number, and the check refuses them, naming the replacement (a pair whose number names no
question - one merged away before this feature - names nothing and passes in a landed spec, as a range does; anywhere
else the retired argument is refused, whatever its number, because a live file using it is stale). (2) The check reads every tracked file except what FR-017 does not edit: the GM's own words (`request.md`, a SOURCE block,
a quotation of the GM in the docs' form `*"..."*`); a README, whose stale references are listed in
`readme-correction-offered.md` until the GM rules on them (constitution XVII); the mapping (`moved-303.json`,
`migration.md`); and the guard-replay corpora under `scripts/fixtures/` - verbatim records of commands sessions ran,
restored to their words after the sweep touched them. Within the rest, six files are REFUSAL DATA (the check and its
test, the hook helper `_hm_record.py`, the record-edit and check-bundle hook suites, and the record test proving a
Markdown-era token is reported), whose retired forms are what they
prove refused or re-aimed; and a test, a hook suite or a script's selftest is a FIXTURE, which builds a record of its own,
so a new-form question file it names need not exist here - but a retired form in a fixture is refused like anywhere
else, since a test using an old path for any other reason is stale. A retired directory is caught written with or
without its slash (a page directory's name followed by a slash, by a quote as code builds a path, or by a comma in prose), and four passes of the
sweep, each from what the check found, rewrote them all. (3) A whole-page pointer the sweep
turned into a section pointer was checked for sense in code and docs; where the sweep's directory pattern had glued a
Markdown-era path onto a section id, the original text was restored from the commit before the sweep (101 places); then
every Markdown-era page path whose page is in the mapping - the record's file names before feature 194 - was rewritten
to its section like any whole-page pointer (277 places, three of them live links in pool notes), and the check refuses
the form; a `.md` name that is no page of the record is not touched. (4) The sweep's edits to landed features' specs and plans make those features' recorded
reviews stale; as feature 301's sweep did (its FR-027), the push passes the review and plan gates with their escapes and
the reason logged - a mechanical rewrite of pointers, reviewed here, not a change to what those features decided.

**D9 - Tools.** Every `PAGE=<p> SECTION=<q>` becomes `Q=<NNNN>` (one or more questions: a number names both of a question's pages, a
file name one page); a whole-page
`PAGE=<p>` becomes `IN=<section id or tag>`; `_hm_record.py` gains the one selection function every tool calls
(`select(Q, IN) -> stems`). Hooks (`check-bundle-hooks.sh`, `record-edit-hooks.sh`) emit the new commands; briefs name
`Q=` items; `_brief_load.py` parses both a brief's `Q=NNNN` and its numbers. `make fragment-move FROM= TO=` renames a
stem (all its files) with every pointer.

**D10 - Retired machinery.** `record/split.py`, `store.write_fragments`, `store.write_notes_fragments` and
`make record SPLIT=` are one-time migrations of feature 258 with nothing left to migrate; they are deleted with their
tests rather than ported. `COLLECTIONS` and both its copies go.

**D11 - The tag table for the GM.** The migration writes `tags.md` in the feature directory: per stem, its number, title,
subjects, settings, level, home section and the convention ruling (FR-008, FR-008a), generated from the fragments, so it
cannot disagree with them.

**D12 - Peers.** Before landing, every clone in `.clones/` is checked for unpushed commits touching `research/`; any
found is reported in the closing notes. After landing, their old paths are refused at their push with the new path
named (FR-018), which is the mechanism, not a manual merge.

## Phases

1. **Data**: `tags.json`, `contents.json`, the reviewed tag table (R8).
2. **Migration script** (`scripts/_record_flatten.py`, `make record-flatten`, one-time, kept until landing then
   deleted with its test): numbers, moves, links, notes copies, markers, openings, confusables, `moved-303.json`,
   `tags.md`, `migration.md`. Tested on a fixture record first, then run on the real one.
3. **Engine**: `record/questions.py` (stems, markers, refusals), `record/contents.py` (vocabulary, contents, homing,
   order, refusals), `store.py` reduced to the per-question reading, `site_links.py` (new index), `xref.py`,
   `confusables.py`, `site.py` + `site_pages.py`, `sources.py` (Entry resolution, SITE_PAGES), `citations.py`,
   `tools/footnote_census.py`, `pipeline/record_build.py`. Tests rewritten on flat fixtures; refusal tests first.
4. **Pointer sweep** (`scripts/_pointer_sweep.py` extended) and the pointer check.
5. **Tools and hooks** (R6's inventory), with their tests and `make hooks-test`.
6. **Docs** (R6's fourteen files) and agent contracts.
7. **Verify and land**: `make record CHECK=1`; SC checks as tests where mechanical; pool map links; `make done`; the
   baseline compared; peers checked; push.

## Project Structure

Documentation: `specs/303-research-organization/` - spec, plan, research, data-model, contracts/, quickstart, tasks,
tags.md, migration.md. Source: `.claude/skills/diagram/research/` (data), `.claude/skills/diagram/l7r/diagram/interactive/record/`
(engine), `scripts/` (tools, hooks), `.claude/skills/diagram/tests/` (tests).
