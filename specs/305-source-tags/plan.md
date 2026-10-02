# Implementation Plan: source tags

**Branch**: none (main, clone `diagram-organization`) | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)
**Input**: the accepted spec (FAITHFUL at round 1) and [request.md](request.md)

## Summary

There are two new data files beside the record's vocabulary:

- `research/source-tags.json`: three facets (period, region, kind), each value with a label and a standard
  explanation, plus the fixed Setting canon label.
- `research/source-sections.json`: the works sections in order, each with a rule over a work's primary tags.

Each registry entry states its tags in a last-line marker. A new engine module, `record/source_tags.py`, loads,
checks and applies them. The build groups every list of works by section and puts the labels under each work's
heading, and the existing tooltip box shows each label's explanation. `make reserve KIND=registry` takes `TAGS=`. The
`source-applicability` contract gains a derived block holding the vocabulary and a rule for judging tags. The 2,126
entries are classified, and their limits paragraphs trimmed, by Sonnet batches. Mechanical checks and a stratified
Opus sample hold that work.

## Technical Context

- **Language**: Python 3.12 (engine `l7r/`, tools `scripts/`), JSON data, HTML fragments, one JS file.
- **Testing**: pytest through `make quick` / `make done`; `make hooks-test` for the reserve path; 100% engine coverage.
- **Target**: `make record` and `make record CHECK=1` (the push), the gate's record tests.
- **Constraints**: no file past 1,000 raw lines; two builds byte-identical; nothing reads the built site.
- **Scale**: 2,126 entries, 16 of them canon (research R1).

## Performance bookends

There is no generator change. `make record` is timed before (on the baseline worktree) and after. A slowdown over 10%
is diagnosed before landing, and both figures go in the closing notes.

## Constitution Check

- **I, II**: N/A. The record site's look gains small labels. Its shell and stylesheets are otherwise unchanged.
- **III, IV, V, VII, VIII, IX**: N/A. There is no pool content and no in-world content. No SOURCE block, `request.md` or
  canon file is touched, and the trim skips nothing of the GM's because no registry entry holds the GM's writing (canon
  entries are untouched: R5).
- **VI**: PASS. Every task names its verification. The closing phase runs `make record CHECK=1`, `make hooks-test`,
  `make done`, and the SC-004/005 sample.
- **X**: PASS. The refusals (FR-010) are written as failing tests first. Everything passes ruff and pyrefly at 100%
  coverage. `source_tags.py` is a new small module, so `site.py` (361 lines) and `citations.py` grow only by their
  calls.
- **XII**: N/A for the world. No rendering decision is made about a map. The record's classification decisions are
  in the spec's Decisions Recorded and in D3 below.
- **XIII**: PASS. The baseline is `make done` on unmodified main in a detached worktree (`/tmp/base305`), and its
  result is recorded in the closing notes. There are zero new failures at landing.
- **XIV**: defects found on the way are fixed in this feature.
- **XVI**: the decisions below are reviewed by `spec-fidelity` (MODE 4) before any task is ticked.

## Decisions

**D1 - The data files.** `research/source-tags.json` has the keys `period`, `region` and `kind`, each a LIST of
`{id, name, description}`. A list fixes the order the labels are shown in. A `canon` object holds the fixed label.
`research/source-sections.json` is `{"sections": [{id, title, description, canon?: true, takes: [clause, ...]}]}`. A
clause is an object over `period`, `region` and `kind`, each a value or a list, and it tests the work's PRIMARY value
of that facet. A clause matches when every facet it names matches. A section with `canon: true` takes the canon
entries and has no `takes`. Section ids carry the prefix `works-` so they cannot collide with a registry key (the
build's id check claims them).

**D2 - The marker** (research R6): the last line of the entry,
`<!-- tags: period=a[,b]; region=x[,y]; kind=k[,l] -->`. Each facet appears once and the first value is primary. A
canon entry carries no marker. A non-canon entry with no marker, an unknown value, a facet missing or repeated, or
primary tags no section takes is refused (FR-010). Every refusal is gathered into the build's error list, so one run
names them all.

**D3 - The vocabulary text** is the session's (GM message 2 for the cut-offs). It is written once in
`source-tags.json`, and the docs and the agent contract derive from it or point at it. The cut-offs and their logic
are in each period's explanation:

| Region | Premodern | Modern preindustrial | Present day |
|---|---|---|---|
| Japan | before 1868 (Meiji Restoration: foreign trade, factory goods, the 1873 land tax) | 1868 to about 1955 | after about 1955, when farm machinery and the consolidation of fields spread |
| China | before about 1895 (treaty-port factories, railways) | about 1895 to about 1950 | after land reform (1950) and collectivization |
| Korea | before 1876 (the ports opened) | 1876 to about 1950 | after land reform and the war |
| Other East Asia | before colonial rule or annexation brought factory goods and reforms: Vietnam before the French conquest (about 1860-1885), Ryukyu before annexation (1879), Taiwan before Japanese rule (1895) | from then to about 1950 | after about 1950 (land reforms, war, mechanization) |
| Europe | before about 1800 (enclosure, new crops, the first factories and canals) | about 1800 to about 1950, while the countryside was still worked by hand and horse but bought factory goods and shipped by rail | after about 1950, when the tractor and chemical fertilizer replaced the horse and manure |
| Elsewhere | before the region's countryside was reached by railways, factory goods or colonial cash cropping | from then until farm machinery spread, about 1950 in most places | after that |
| General | the period of its evidence, by the rule of the region it comes from; a work about facts that do not change with the era is not period-bound | | |

Every cell of this table is written into the period explanations in `source-tags.json`, so a reader hovering a label
sees the cut-off for every region and the reason for it. No cut-off reasoning lives only in a batch note: a
classifier that finds a source the table does not settle stops and lists it for the session, and the session extends
the explanation before tagging it.

**D4 - The sections** are FR-007's eight, in that order, in `source-sections.json`. "Beyond East Asia, and general
works" takes the primary regions Europe, elsewhere and general. "Not period-bound" comes before it and takes the
primary period timeless first, so a timeless botanical work tagged `general` lands under Not period-bound.

**D5 - Rendering.**

- **Labels**: under a work's heading, `<p class="srctags">` holding one `<span class="srctag srctag-<facet>"
  data-def="..." title="...">Label</span>` per value. The facets are shown in the order period, region, kind, and a
  canon entry shows one canon label. `record.js` gives `span.srctag[data-def]` the glossary's hover handler, so the
  explanation shows in `#fntip`. `site.css` styles the labels as small outlined chips.
- **Grouping**: a question page's foot "Works cited here" becomes a sequence of `<h3 class="works-section">` headings,
  each followed by its description in italics and its works as `<h4 id="work-<key>">`. Within a section, works keep
  first-citation order. The registry part of `all.html` and `sources/index.html` group the works-cited registry group
  the same way, with works in registry order inside a section. The registry pager walks the works in that grouped
  order. A section holding nothing on a page is not shown.
- **The marker** is stripped from every shown copy of an entry.

**D6 - The engine module.** `l7r/diagram/interactive/record/source_tags.py` holds:

- the loaders, `load_vocabulary` and `load_sections`;
- `parse(text, where, vocab)`, which returns `SourceTags | None`;
- `home(sections, tags, canon)`;
- `labels_html(tags | canon, vocab)`;
- `strip_marker(html)`;
- `Catalog`, built once per build from the registry entries: `section_of(key)`, `labels(key)` and `errors`.

`citations.works_html` takes the catalog and groups by it. `sources.registry_entries` gains a `tags` field, the raw
marker, so the catalog needs no second parse of the registry.

**D7 - `make reserve KIND=registry ... TAGS="period=..; region=..; kind=.."`.** `reserve-prefix.py` checks the tags
against `source-tags.json`, refusing an unknown value with the allowed list, and writes the marker as the stub's last
line. Without `TAGS=`, the stub carries `<!-- tags: period=<period>; region=<region>; kind=<kind> -->`, which the
build refuses until it is filled. The `Makefile` passes `TAGS` through (a guard-file edit, with its `GUARD_EDIT_OK`
reason).

**D8 - The agent contract** (FR-012). `.claude/agents/source-applicability.md` gains:

- a section "Tags", stating the rule: judge each tag against the entry and its source, period by the evidence, and
  flag a write-up that restates a limit its labels state;
- a derived block, between `<!-- source-tags: DERIVED ... -->` markers, holding every value's label and explanation.

`make source-tags-contract` rewrites the block. A test fails while the block differs from `source-tags.json`, naming
the command. The report's verdict line gains `tags RIGHT / WRONG (facet: should be X)`, and a wrong tag ends with an
EDIT block on the marker line.

**D9 - The docs** (FR-013). These state the rule in a few lines and point at `source-tags.json`:

- `research/CLAUDE.md`, under "every cited work says what it is";
- `docs/research-doctrine.md`, in the write-up rule;
- `container-scripts/page-session-rules.md`, in the new-entry rule;
- the root `CLAUDE.md` Research paragraph, one clause: a source carries tags from `research/source-tags.json`, and
  `research/source-sections.json` groups the works.

**D10 - The migration** (research R3-R5) is spec-local tooling under `specs/305-source-tags/migrate/`, never engine
code:

1. `extract.py` writes the batches.
2. The 22 Sonnet batches are dispatched in waves of 6, each returning JSON lines.
3. `apply.py` checks every line: the vocabulary, R4's no-new-content rules and R3's consistency lists. It writes the
   markers and the passing trims, and lists every refusal and every consistency flag.
4. The session works the lists by hand.
5. The build check is switched on only when the registry passes. Until then the code lands behind nothing: the code
   and the data land together in one push.

**D11 - The check.** The sample is drawn stratified (at least five entries for every period and region value, where
that many exist), at least 60 entries in all. Each key is bundled with `make check-bundle KEY=`, and the bundles are
dispatched to `source-applicability` in about six agents of ten keys. Every WRONG tag and every repeated or lost limit
is fixed. A pattern the sample shows (for example, "Meiji-era surveys tagged premodern") is swept by a grep across the
registry and fixed wherever it holds.

## Phases

1. **Setup**: the baseline worktree and its `make done`; time `make record`.
2. **Engine (TDD)**: `source_tags.py` with its tests, red then green; `citations` and `site` grouping and labels; JS
   and CSS; the build's refusals.
3. **Tools**: the `reserve` `TAGS=` support with its hook test; the contract block and its test; the docs.
4. **Migration**: extract, classify, apply, the hand lists, the vocabulary finalized (a value added only if a real
   group needs it, FR-002).
5. **Check**: the SC-004/005 sample and its sweep; SC-002's three seeded faults (as tests); SC-003 by a script over
   the built site; SC-006's figure.
6. **Close**: `make done`, `make record CHECK=1`, the timing, the closing notes, the push.

## Project Structure

```text
.claude/skills/diagram/research/source-tags.json              new - the vocabulary
.claude/skills/diagram/research/source-sections.json          new - the sections
.claude/skills/diagram/research/sources/010-works-cited/*     each gains its marker; the limits paragraph trimmed
.claude/skills/diagram/research/assets/{record.js,site.css}   the label hover; the chips
.claude/skills/diagram/l7r/diagram/interactive/record/source_tags.py   new
.claude/skills/diagram/l7r/diagram/interactive/{citations,sources}.py, record/site.py   grouping and labels
.claude/skills/diagram/tests/interactive/test_source_tags.py  new; test_record_site.py extended
.claude/agents/source-applicability.md                        the Tags rule and the derived block
scripts/reserve-prefix.py (+ its test), .claude/skills/diagram/Makefile   TAGS=; source-tags-contract
docs, research/CLAUDE.md, container-scripts/page-session-rules.md, CLAUDE.md   the rule
specs/305-source-tags/migrate/                                the one-time tooling and its outputs
```

## Complexity Tracking

None.
