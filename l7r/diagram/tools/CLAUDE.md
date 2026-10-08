# `tools/` - diagnostics, audits and by-hand utilities

Things you RUN when a map comes out wrong or a number needs measuring, and the builders and audits the gate and the
record call. **Nothing in this directory is imported by a generator or by the engine** - that is the membership rule
for the folder, and it is what makes these modules safe to change without thinking about map output. (They are still
inside `gencache.engine_files()`, deliberately: the cache stays conservative rather than clever about what can reach a
gen. See [`../pipeline/CLAUDE.md`](../pipeline/CLAUDE.md).)

Run them through their `make` targets at the repository root (named in the table; `docs/make-targets.html` lists each
target's arguments). A tool with no target of its own is run by a test or by another target, never by a bare
interpreter (`scripts/make-only-hooks.sh` refuses one).

## Which tool answers which question

| You are asking | Reach for |
|---|---|
| Who put this thing here? What refused to put anything here? | `why_placed` - `make why-placed GEN=... AT=x,y` / `REFUSED=x,y` |
| Is there too much empty space in this Mode A compound? Does its SVG break a geometric rule? | `pack_audit` - `make pack-audit` (its own [index](pack_audit/CLAUDE.md)) |
| What does each declared Mode A type require, as a table? | `building_programs` - `make building-programs` (writes `docs/buildings/programs.md` between markers) |
| Is drawn ground cover standing somewhere the engine's keep-outs should have stopped it? | `scatter_audit` (held by `tests/tools/test_scatter_audit.py`); `make scatter-bases` lists a map's scatter bases |
| Does using the generation cache ever change what a map looks like? | `cache_audit` - `make cache-audit` |
| I fixed one hamlet - does the fix generalize across a cohort, and what exactly collides? | `cohort_audit` - `make cohort N=... [SEED=...]` |
| Regenerate and check the pool, choosing the scope from how the last run went | `mapcheck` - `make maps` |
| Which modules are on the HAMLET PATH and owe 100% coverage? | `hamlet_floor` - a phase of `make test-full`, with no make route of its own |
| Which engine lines does only ONE rolling test context reach? | `roll_audit` - `make roll-audit` (feature 216) |
| How many things does each check of a roll compare against, and which compare against too many? | `overlap_census` - `make census` |
| What does the map look like after each placement stage, and why is that stage there? | `placement_stages` - `make placement-stages` |
| I lit one class on the page - which OTHER classes' pixels changed, and by how much of each? | `page_lit` - `make page-lit` (`VECTOR=1` zooms past the raster switch, feature 245) |
| Two renders of this map: how much differs, by how much, where, and on whose ink? | `picture_diff` - `make picture-diff` |
| Who answers the pointer over each class's visible ink - its own class, or another's hit box? | `hit_share` (feature 294 B6; the gate holds every shipped map to it) |
| Which classes does a page draw see-through, and is a broadleaf crown painted over a conifer? | `see_through` (feature 294 B5; the declared table is `settlement/see_through.py`) |
| Does a marsh meet the open ground on a ruled or plumb line, where a reader sees it? | `marsh_edges` (feature 294 B2; the visible free edge from the page's id map) |
| What does a hand-drawn Mode A sheet look like with its captions placed? | `make sheet-render SHEET=<svg> OUT=<png>` - the placer is `labels/hand_sheet.py`; `caption_decl` was the one-time migration of a sheet's captions from hand-seated to declared (feature 286) |
| A map's canonical counts, in the block its `.notes.md` carries | `notes_census` - `make notes-census` |
| The engine's and the Mode A procedures' research CLAIMS, read from the source | `claims` - behind `make claims-owed`, `claims-bundle`, `claims-checked`, `claims-report` (feature 316) |
| The record's footnotes counted by kind - what is owed | `footnote_census` - `make footnote-census` |
| Assemble or check the glossary from its per-term files | `glossary_asset` - `make glossary` |
| Build or check the record's site from its per-entry fragments | `record_asset` - `make record` |
| The source vocabulary derived into the `source-applicability` contract | `source_tags_contract` - `make source-tags-contract` (feature 305) |
| A performance snapshot of the reference hamlet, its bands, its profile and its review records | `perf_snapshot` (`make perf`), `perf_bands` (`make perf-report`), `perf_profile` (`make perf-profile`), `perf_review` (`make perf-explain` / `perf-review` and the rest) |
| How long does this loop take, and where does the time go? | `make audit`, `make durations`, `scripts/_gatecost.py <target>`; the frozen ledger is `dev/timings.md` |

Each module's own docstring carries the WHY it exists, usually with the incident that produced it. Read that before
extending one. The operational guidance for `why_placed` and `open_seat` is [`dev/diagnostics.md`](../../../dev/diagnostics.md).

## The rule these share: a diagnostic OBSERVES, it never restates

`why_placed` reads its refusal causes off the real `_in_blocked` / `_near_corridor` / `_hard_clear` as they return; it
re-implements no rule, and that is not style. A predecessor that re-derived every rule as its own predicate drifted
**within a single session** - a relaxation made to satisfy one map persisted and put Nagahara's boundary stone in a
field off the highway. A tool that re-derives a rule will eventually disagree with the placer and then tell you the
wrong thing with total confidence. To ask where a feature may go, use `open_seat` and `why_placed`, which read the
placer's own refusals rather than a second opinion about them.

`pack_audit` and `scatter_audit` are the exception that proves the rule: Mode A has no manifest and scatter is
draw-time ink, so both parse the rendered SVG. They are the source of truth for their own questions rather than a
restatement of someone else's.

## A tool whose input is a PATH will be broken by a refactor - point it at a directory

`cache_audit` mutates a numeric literal and demands a cached sweep and a fresh sweep agree. Its mutation target was once
a single hand-picked FILE, invalidated twice by package splits - each time the tool crashed on its next mandatory run.
The target is now the set of trees that DRAW a map (`settlement`, `waterfields`, `sitegen`, `hamletgen`), and the site
is chosen from what the audited maps actually EXECUTE, measured by a coverage pass over the gens. To carry to any tool
of the same shape:

- **A directory target cannot be invalidated by a split inside it.**
- **Choose from what runs.** Literals in code the maps never run change no byte, so a trial on one proves nothing while
  printing the same `[OK ]` as a real one.
- **State the membership rule at BOTH ends.** Coverage's own config is not the rule: `--include` is ignored when
  `[tool.coverage.run] source` is set, and a `source` list can omit a tree that draws every paddy.

## Coverage

**Everything here owes 100%, the day it lands** (GM 2026-09-02, constitution Principle X clause 5: *"A new tool
absolutely should silently owe one hundred percent coverage the day it lands ... For tools, for our settlement
generation, for the automated checks on our hand drawn diagrams, for everything."*). The measured surface is DERIVED -
`source = ["l7r"]` in `pyproject.toml` - so the way to not owe coverage on something is to not ship it. A boundary that
genuinely cannot be reached is argued at the point of change, like any other exclusion.

For a tool whose work is a SUBPROCESS or a BROWSER: the pure half is tested directly and the driving half where it can
be driven - `page_lit`'s attribution on arrays and its `measure` on the synthetic page the browser tests already open
(`tests/full/interactive/page_browser/`, in a viewport small enough that the page opens in raster mode),
`picture_diff`'s arithmetic on synthetic images and its rendering through resvg on a 40x40 document.
