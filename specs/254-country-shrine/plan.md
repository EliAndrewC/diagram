# Plan - feature 254, the country shrine and checks in two layers

**Branch**: none (`export SPECIFY_FEATURE=254-country-shrine`) | **Date**: 2026-09-19 | **Spec**: [spec.md](spec.md), FAITHFUL at round 2 | **Research**: [research.md](research.md) R1-R4 (the pass), D1-D13 below (the plan's decisions)

## Summary

Three deliveries, in the order the spec's user stories put them. (1) A Mode A building TYPE becomes
one declaration - a JSON asset the engine reads - and the five places that hardcode the magistracy
derive from it; the audit's checks are registered with the types each applies to, read the precinct
from the sheet's own marker, and every live Mode A sheet is swept by the gate, each check proven on a
red fixture. (2) The country shrine's program lands in the catalog from the declaration, and the record
gets its two new sections, the corrected village section, the footnotes and the registry entries,
verified by the agents in the order the doctrine sets. (3) One exemplar, the country shrine of
Hoshigaoka's village district (the reference village, whose names the GM dictated on 2026-08-29), is
hand-drawn to the program, reviewed twice, and stands under `pool/country-shrines/`.

## Technical context

Python 3.12, the diagram engine under `.claude/skills/diagram/l7r/diagram/`, pytest through `make`
(quick with testmon; `make done` the full gate at 100% coverage over `l7r`), ruff, pyrefly. No
generator changes: Mode A sheets are hand-authored SVG at 3 px = 1 ft, rasterized by resvg. Content
as data follows feature 207 (`interactive/content.py` reads `interactive/assets/*.json`; a JSON asset
sits outside the engine key). Storage is files in git. The one performance-relevant addition is a gate
test that parses six small SVGs.

**Single-artifact target**: the exemplar, `pool/country-shrines/hoshigaoka-shrine/hoshigaoka-shrine.svg`
(a resvg raster of a 6 KB sheet, under a second). Every phase below is two steps: the reference sheet
(Ochiba for the magistracy, the exemplar for the shrine) then the pool (all six sheets under `make quick`).

## Performance bookends

N/A for the generator: no settlement generator is touched, so `make perf` bookends measure nothing this
feature changes. What IS measured: the new sweep's cost, taken once with `scripts/_gatecost.py` on the
gate's duration record after the sweep lands and written to `measurements.json` as `m:sweep-cost`
(spec SC-002); the gate's ratchet holds it thereafter.

## Baseline (constitution XIII)

Before the first edit: `git worktree add --detach /tmp/base HEAD`, then `make quick ALL=1` and
`make hooks-test` there, the counts recorded in `measurements.json` (`m:baseline-quick`); each later
failure is checked against the clone, because the worktree carries no gitignored renders. Zero new
failures at merge; a pre-existing failure is ledgered.

## Constitution check

- **I, II**: N/A - no UI in this repository.
- **III. Pool data conventions**: the pool gains a tier folder `pool/country-shrines/<name>/` with the
  three files a magistracy has (`.svg` tracked source, `.gen.py` rasterizer, `.notes.md`); no new
  markdown-with-YAML kind; nothing city-specific is baked in (the exemplar is named for a village
  district, the program is generic).
- **IV, V**: PASS - no SOURCE blocks are added, moved or touched.
- **VI. Verify before done**: each task lists its verification; the exemplar runs `building-review`
  and `size-audit` (ledger rows); Python runs `make quick` while iterating and `make done` once at the
  end; every phase is reference-then-pool.
- **VII, VIII**: PASS - generic program framing; the notes file's in-world lines are direct voice.
- **IX. Setting integration**: the canon read is `setting/l7r.md` (the country monk, the Ministry of
  Rites, the registers); no new named figure; the dedication follows the clan patron Fortune the
  record's town rule already uses.
- **X. Python discipline**: ruff, ruff format, pyrefly, red-green for every check (the red fixture IS
  the red), 100% coverage over `l7r` the day it lands; no file past 1,000 lines (`checks.py` is about half the bar today;
  the registry and the three new shared checks are a new module `registry.py` in the package, not
  appended); the one overlap check this feature adds (structures overlapping structures, D8) is an
  O(n log n) sweep over sorted rect edges, built once per sheet, over at most a few dozen rects - no
  spatial index is warranted at this size, and the plan says so rather than pretending one is needed.
- **XII. Grounding bookends**: opening bookend done - `research.md` R1-R4 states the historical
  reality for every element (China first where the record has it, Japan corroborating, and Japan-first
  for compound interiors by the Mode A doctrine), whether the design matches it, and what determines
  it; the closing bookend is Phase 5's re-read of the exemplar PNG against R1-R3. Every rendering
  decision is in the spec's Decisions Recorded table with its class.
- **XIII**: the baseline above; the pool sweep of scripted maps is untouched by this feature.
- **XIV**: defects found in the audit while registering its checks are fixed in the same work (D9).
- **XV, XVI**: the chain runs unattended; every decision below is within the spec or marked.
- **XVII**: no README is written; `buildings.md` and `programs.md` are skill docs, not READMEs.
- **XVIII**: no shell guard is added. The one test that acts as a guard (the type-name census, D2)
  ships with a red proof: delete a declaration line and watch it fail.

## Decisions this plan makes that the spec left open

- **D1 - where the declaration lives and what it holds.** `l7r/diagram/buildings/types.json`, read by
  a new `l7r/diagram/buildings/types.py` (`load_types()`, `by_tier()`, `hand_drawn_tiers()`), a JSON
  asset outside the engine key like feature 207's. One object per type: `tier`, `title`, `program`
  (the type's `programs.md` heading), `hand_drawn` (bool), `generated_exceptions` (stems whose SVG is
  generated inside a hand-drawn tier - the two magistracy examples), `required` (a list of items, each
  with `id`, `label` - a case-insensitive regex the sheet's text must match - and `band_ft`: `w`, `h`
  min/max or `area_min`/`area_max`, plus `optional: true` for a knob-governed item), `checks` (the
  per-type check names that apply), and `notes` (the why, in prose, rendered into the docs). Within the
  spec (FR-001).
- **D2 - the consumers derive, and a census holds them to it.** `poolmaps.classify` returns `compound`
  when the gen's tier is a declared type (the `COMPOUND_GENS` list is retired; a gen in an undeclared
  tier that imports no engine stays `unknown`, loudly); `pool_index.MODE_A_DIRS` and its tier section
  titles come from the declaration (`pool_index_text.json` keeps only the Mode B tiers); `_size_table.py`'s
  usage line names `pool/<tier>/` generically; the sweep iterates the declared tiers. A gate test,
  `tests/test_building_types.py::test_no_type_name_outside_its_declaration`, greps `l7r/` and
  `scripts/` for every declared tier name and fails on a hit outside `types.json`, the pool, the
  fixtures, the tests and the docs (SC-001). Within the spec.
- **D3 - the ignore rule per tier.** `.gitignore` replaces the three per-file negations with one
  negation per hand-drawn tier (`!.claude/skills/diagram/pool/magistracies/*/*.svg`,
  `!.claude/skills/diagram/pool/country-shrines/*/*.svg`) followed by a re-ignore per declared
  generated exception. `tests/test_building_types.py::test_ignore_file_matches_the_declaration` reads
  both and fails on a difference; `render_cache.is_cacheable` follows automatically because it asks
  `git check-ignore`. Within the spec (FR-001, edge case 2).
- **D4 - the precinct is a marked element.** A Mode A sheet marks its precinct with `id="precinct"` on
  the rect (or rects) that bound the ground the checks reason over; the parser reads those and no longer
  requires the earth-court fill, and raises naming the sheet when none is marked. The five magistracy
  SVGs gain the attribute on their existing court-earth interior rect (a source edit, no geometry
  change; their PNGs are byte-identical after, checked with `tools/picture_diff.py`). The shrine's
  precinct is the fenced rectangle, its ground a new swept-gravel pattern the parser does not need to
  know. Within the spec (FR-002, US1 scenario 3).
- **D5 - a check registry, with fixtures as data.** `tools/pack_audit/registry.py` holds
  `CHECKS: tuple[Check, ...]`, each `Check(name, run, types, fixture, fix)` - `types=None` for the
  shared layer, a frozenset of tier names otherwise; `fixture` the red fixture's filename under
  `tests/fixtures/`; `fix` the compliant-fix sentence a failure prints. Vacant rectangles, region density and aligned gaps are the report's figures, not pass/fail, and are not registered; coverage and perimeter hugging ARE registered as the magistracy's checks (D6), because the spec names them as such. `report.py` composes from the registry. Within the spec
  (FR-003, FR-005).
- **D6 - which existing checks are the magistracy's.** Per-type under `magistracies`: `coverage_band` (the jin'ya band of 37-42% the report already prints, made pass/fail), `perimeter_hugging` (its floor DERIVED from the five pool sheets - the lowest shipped value less a margin, measured and recorded as `m:hugging-floor` before the check lands; if no honest floor separates the five from a defect, that is an exception put to the GM, never a silent demotion), `notice_board_adrift`, and the two-court zoning check (new, D8). Each with a red fixture (a magistracy sheet with its buildings pulled into the center, and one with a building deleted below the band). Shared: `occluded_foreground`, `overlapping_labels`, `dark_on_dark_labels`,
  `floating_doors`, `structures_on_walls`, `passage_blockers`, `wall_openings` (against the width a
  comment states), `orphan_group_labels`, `fire_water_adrift`, `tubs_in_buildings`, `tubs_on_wells` -
  the fire-water three declare BOTH types by the spec's ruling, which in the registry is
  `types=frozenset({"magistracies", "country-shrines"})`, and a type whose program has no fire-water
  would simply not be listed. Within the spec (FR-003, round-1 item 2).
- **D7 - program completeness and size bands are generic code over the declaration.**
  `check_program(plan, type)` matches each required item's label regex against the sheet's labels and
  reports the missing; `check_bands(plan, type)` pairs each matched label with the nearest structure
  rect (the size table's nearest-label pairing, moved from `scripts/_size_table.py` into
  `tools/pack_audit/labels.py` so the script and the check share one pairing - the script becomes a
  thin caller) and reports a footprint outside its band. A combined hall-and-dwelling (knob 1's
  default) is declared in the notes as `form: one roof`, which the check reads to count one building as
  both items. Within the spec (FR-003, edge case 3).
- **D8 - three new shared checks and one magistracy check.** Shared: `structures_overlap` (any two
  structure rects intersecting by more than the rounding floor `WALL_OVERLAP_MIN_PX` - the GM's own
  example, "whether different shapes end up overlapping with each other"; a sorted-edge sweep),
  `scale_bar_present` (the `30 ft` label and its bar), `viewbox_cropped` (no drawn ink outside the
  viewBox and no margin past 25 px on any side). Magistracy: `two_court_zoning` (a divider band exists
  and the hearing-court sand lies gate-side of it). Shrine (per-type, `country-shrines`):
  `sanctuary_on_axis` (the sanctuary rect's center within a tolerance of the approach axis, behind the
  hall), `arch_on_approach` (the arch glyph straddles the approach where it crosses the fence),
  `well_clear_of_arch`, `fence_not_wall` (the precinct boundary is drawn in the fence stroke, not the
  compound-wall stroke). Each with a red fixture cut from the pool sheet. Within the spec (FR-002,
  FR-003, FR-005).
- **D9 - defects the registration turns up are fixed now.** Registering the existing checks over the
  five magistracy sheets may fire on a shipped sheet (the pool has never been swept by the gate). Each
  firing is a defect in the sheet or in the check; fixed in this work, recorded in the sheet's notes
  Review log, never ledgered as pre-existing (constitution XIV). Within the spec (FR-004).
- **D10 - the gate sweep.** `tests/gate/test_mode_a_sheets.py`, parametrized over
  `poolmaps.bundles(kinds=("compound",))`, runs every registered check whose `types` covers the
  sheet's tier and asserts none fires, the message naming sheet, check and fix; listed in the gate's
  roster (`tests/fixtures/gate_check_names.json`). Its cost is measured (`m:sweep-cost`). Within the
  spec (FR-004, SC-002).
- **D11 - the program prose is rendered from the declaration, for BOTH types.** Each type's entry in `programs.md` carries its knobs, anchors and staffing in hand-written prose around a required-items table between `<!-- types.json:<tier> -->` markers written by `make building-programs` (`CHECK=1` fails the gate when stale, like `make glossary`); the table's rows are the declaration's items with their labels, bands, classes and whys. The magistracy's existing required-program bullets are converted: the per-item reasoning they carry moves into each item's `why` in the declaration (the field exists for exactly this), and prose that is about the type rather than an item (the cart route, the guest-door rule, the divider gate) stays as prose above the table. The plan's first draft kept the magistracy's list hand-written; the plan review ruled that a narrowing of FR-001's "declared once ... and the docs render from", and it is withdrawn. Within the spec.
- **D12 - the exemplar.** `pool/country-shrines/hoshigaoka-shrine/`: the country shrine of Hoshigaoka
  village district. Knobs: form one roof (the GM's default); bell absent; dedication the clan patron
  Fortune named in Hoshigaoka's notes; grove west and burial ground east (the site's water-mouth side,
  read from Hoshigaoka's map); wealth average (thatch). Its particulars beyond the program are left open
  in the notes for the GM. Within the spec (FR-015, Assumptions).
- **D13 - the record's mechanics.** Two new `<h2>` sections on `religion-and-death.html` after
  "Where does a village put its shrine, and how big is it?"; footnotes fn-143 onward on
  `citations/religion-and-death.html`; registry entries in `SOURCES.html` for every page read (FR-014's
  list), each with the two write-ups; glossary terms (kuri, honden, haiden, bettō, jingūji, miyaza,
  jochi, shasō) in `assets/glossary.json`; `make citations` and `make glossary`; the village section's
  revision; `interactive/classes` entries for the village shrine gain the two new questions by `Entry:`
  name. The agents, in order: `source-reader` on the two new sections (READ per claim); `make
  quote-verbatim PAGE=religion-and-death` then `quote-check`; `make record-prepass` then
  `record-format`; `source-applicability` over the new keys in three dispatches by group (Japanese
  encyclopedia and cultural-property pages; Chinese pages; the RPG wiki); `entry-drift` on every class
  entry naming the revised village section. Within the spec (FR-012 to FR-014).

## Phases

**Phase 0 - baseline and declaration** (`research: rendering` - tooling, nothing physical behind it). The worktree baseline (XIII).
`types.json` with both types; `types.py`; `poolmaps`, `pool_index`, `_size_table`, `.gitignore`
derived (D2, D3); the census and ignore tests red then green; `make quick`.

**Phase 1 - the parser and the registry** (`research: rendering`). `id="precinct"` on the five
magistracy sheets (D4, PNGs byte-identical); the parser reads it; `registry.py` with the existing
checks registered and their fixtures named (D5, D6); the three new shared checks and the magistracy's
zoning check with fixtures (D8); `report.py` composed from the registry; `make pack-audit` unchanged in
use. Reference: Ochiba; pool: the five magistracies. Defects fixed as found (D9).

**Phase 2 - the sweep** (`research: rendering`). `test_mode_a_sheets.py` (D10); the roster; the cost
measured and recorded (`m:sweep-cost`); `make quick` green on the five.

**Phase 3 - the program and the shrine's checks** (`research: physical`; the pass is R1-R3, the boxes below). The declaration's `country-shrines` entry (D1); `programs.md`'s entries for both types with their rendered blocks (D11); the reviewer prompts `.claude/agents/building-review.md` and `.claude/agents/size-audit.md` name the program by type and read the type's rendered block (FR-006); `buildings.md`: the vocabulary for the sanctuary, the arch, the fence, the gravel ground and the
grave markers, and the "Adding a building type" section (FR-007); the shrine's four checks (D8) -
their fixtures wait for the exemplar.

**Phase 4 - the record** (`research: physical`). The two sections, the village revision, the
footnotes, the registry entries, the glossary, the class entries (D13); the agents in order; the five
boxes ticked on verification.

**Phase 5 - the exemplar** (`research: physical`). The sheet, the gen, the notes (D12); `make
size-table` then `size-audit`; `building-review`; ledger rows; the four shrine fixtures cut from it;
`make quick` sweeps six; the closing bookend (the PNG against R1-R3); the pool index shows the tier.

**Phase 6 - the gate and the push.** `make done` in the background; `sync-with-main.sh done` - the
delta carries engine code, so the route is GATED.

## Project structure

```text
.claude/skills/diagram/
├── l7r/diagram/buildings/            # NEW package: types.json, types.py (the declaration and its reader)
├── l7r/diagram/tools/pack_audit/     # parse.py (precinct marker), checks.py, registry.py (NEW), labels.py (NEW), report.py
├── l7r/diagram/pipeline/             # poolmaps.py, pool_index.py, pool_index_text.json (derive from the declaration)
├── buildings/programs.md             # both types' required-items tables rendered between markers; + Country shrine
├── buildings.md                      # + vocabulary, "Adding a building type"
.claude/agents/building-review.md, size-audit.md   # the program named by type (FR-006)
├── pool/country-shrines/hoshigaoka-shrine/   # NEW tier: .svg, .gen.py, .notes.md
├── pool/magistracies/*/*.svg         # id="precinct" on the interior rect
├── research/religion-and-death.html  # two sections, one revised; citations/ and SOURCES.html
├── tests/fixtures/*-red.svg          # one per registered check
├── tests/gate/test_mode_a_sheets.py  # NEW: the sweep
├── tests/test_building_types.py      # NEW: census, ignore rule, declaration shape
└── tests/tools/test_pack_audit.py    # registry, new checks
scripts/_size_table.py                # thin caller of pack_audit.labels
.gitignore                            # per-tier negation + declared exceptions
docs/review-ledger.md                 # the exemplar's two rows
```

## Complexity tracking

None: no constitution gate is deferred.
