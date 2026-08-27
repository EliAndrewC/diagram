# Implementation Plan: The Interactive HTML Map

**Branch**: none (`SPECIFY_FEATURE=134-interactive-html-map`) | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

## Summary

Every `add()` into the settlement's record streams learns which **feature class** it draws; the
SVG is written exactly as before (the class rides in a side list, never in the SVG text - FR-010),
and `finish()` writes a second serialization, `<base>.html`, in which each classed primitive is
wrapped in `<g class="f f-<class>">`, with the page's CSS, script, and the explanations of the
classes present on that map inlined. Hover toggles a state on every group of the class; click opens
a modal from the embedded explanation. The class vocabulary and the explanations live in one
registry module; a gate check reports any drawn ink that carries no class.

## Technical Context

**Language/Version**: Python 3.14 (engine + page assembly); the page itself is plain HTML/CSS/JS
with no framework and no external asset (FR-001) | **Primary dependencies**: none new at
runtime; **Playwright + Chromium** as a DEV dependency for the browser test (FR-012; root
`CLAUDE.md`: "install what you need") | **Storage**: the `.html` beside `.svg`/`.png`/`.json`,
gitignored like the PNG (FR-011) | **Testing**: pytest `-n auto`; a Playwright test on
`inashiro.html` | **Target**: a plain `file://` open in a desktop browser |
**Single-artifact target**: `pool/hamlets/inashiro.gen.py` (`make reference`, ~26 s) |
**Constraints**: SVG and PNG unchanged (byte-identical PNG, SC-005); page load < 5 s and
highlight < 100 ms on a 16 MB / ~175,000-element map (SC-004) | **Scope**: Mode B; the hamlet
vocabulary now (spec Assumptions).

## Performance bookends (REQUIRED for any diagram-generator change, constitution VI)

| | label | total | median | worst | notes |
|---|---|---|---|---|---|
| before | `134-start` | - | - | - | NOT TAKEN: scope is LOCKED to the reference hamlet (feature 132, GM 2026-08-27 lock reason) and `make perf` rolls 24 seeds, which the lock refuses. Owed at unlock, exactly as feature 133 recorded |
| after | `134-end` | - | - | - | same; the reference-hamlet generation time (`make reference`, ~26 s) is recorded before and after in `tasks.md` as the one measurement the lock permits |

The engine change is one extra list append per `add()` call plus the HTML write at `finish()`;
the HTML write is measured on Inashiro and recorded in `tasks.md`.

## Constitution Check

- **I**: N/A in this repository per the template - BUT this feature adds a browser page here,
  which the template names as *"the signal to reinstate the gm-assistant entry"*. Recorded in
  Complexity Tracking: the page is verified in a headless browser (FR-012) with a screenshot
  for the GM, and a reinstated Principle I entry is proposed to the GM at the report, not
  written into the constitution by this session.
- **II**: N/A (map style is the skill's doctrine; the highlight style is recorded as a rendering
  decision of the HTML target - research.md R2).
- **III, IV, VII, VIII, IX**: N/A - no pool content of a recurring markdown kind, no SOURCE
  blocks, no in-world prose. The explanations are research prose in the record's own voice,
  citing `research/` entries; nothing named, nothing campaign-tied.
- **V**: PASS - nothing of the GM's is edited.
- **VI**: PASS - each task's verification is named in `tasks.md`; the reference hamlet is the
  single artifact; `make done` (locked scope) before the push; the pool step is owed at unlock and
  is a task; the page is verified in a browser, not by reading its source.
- **X**: PASS - ruff, ruff format, mypy --strict, 100% on the new `interactive/` package, tests
  behavior-named. New files stay under ~1,000 lines: the registry is split by topic
  (`interactive/classes/` - one module per feature family) if it grows past that; predicted
  ~600 lines total. Playwright is pinned via `requirements-dev.in` -> `requirements-dev.txt`.
- **XII**: PASS with the bookends as follows. This feature draws nothing new; it STATES. Opening
  bookend (`research.md` R3): every class explanation is mapped to the `research/` entry it is
  drawn from, with its label, and a class whose record is silent is written as **guess** and
  says so. Closing bookend: the rendered page is opened and each explanation read against its
  entry (task T-close). The `[ ]` "decisions for the reader" box: the spec's Decisions Recorded
  table is filled one row per class at implementation.
- **XIII**: PASS - baseline `make done` (locked scope, ~75 s) on unmodified code in a detached
  worktree before the first edit; SC-005's PNG hash is the regression measure for the render;
  zero new failures at the push.
- **XIV**: any defect met is fixed in this work.
- **XVI**: the spec is reviewed by `spec-fidelity` against `gm-request.md` before Phase 2
  begins (verdict in the spec's Review history).
- **XVIII**: the new gate check ships with a test that proves it fires (SC-006).

## Design

### D1. Classes ride in a side list, never in the SVG (FR-002, FR-010)

`core.py`: the four record streams (`add`, `add_wall`, `add_label`, `add_top`) take
`cls: str | None = None` and append to a parallel class list (`self.out_cls`, `self.walls_cls`,
`self.toplabels_cls`, `self.top_cls`) - index-aligned with the string lists, so a z-index looks up
its class. A context manager `with self.feature("farmhouse"):` sets a default class for every
`add()` inside it (`self._cls`), so a drawing method that emits many primitives for one feature
tags them with one line; an explicit `cls=` wins over the context. The deferred blocks (`_ground`,
`_water`, late water) carry `cls` on their entries and `finish()` builds the class block beside
the string block when it splices. `finish()` then writes the SVG from the string lists exactly as
today - the class lists never touch the SVG text - so the PNG is byte-identical by construction.

**One split hint** (`split=("paddy", "bund")`): a comb paddy is one polygon whose FILL is the
flooded plot and whose STROKE is the bund. The SVG keeps the one polygon; the HTML writer emits
it twice - a fill-only copy classed `paddy` and a stroke-only copy classed `bund` - so the two
highlight separately (US3). The hint is recorded beside the class and applied by the HTML writer
alone.

**Where a draw is one `add()` for two classes** (the farmhouse and its attached shed are joined
into one string in `house()`), the join is split into two `add()` calls. That inserts a newline
between two elements in the SVG text, which changes no pixel; SC-005 checks the PNG hash and a
whitespace-normalized SVG comparison (tags identical in sequence) so the SVG check is stronger
than "looks the same".

### D2. The vocabulary and the explanations are one registry (FR-007, FR-008)

New package `l7r/diagram/interactive/`:

- `classes.py` - `FeatureClass(key, name, covers, siblings: dict[key, str], label, sources,
  what, why)`, and `CLASSES: dict[str, FeatureClass]` - one entry per FR-007 row. `label` is one
  of `accurate | deviation | guess`; `sources` a tuple of `research/SOURCES.md` keys or
  `("not recorded",)`. A test asserts every entry has all fields and every key in the spec table
  is present (SC-007).
- `page.py` - `write_html(basepath, body_strings, body_classes, view, W, H, M)`: wraps classed
  strings, assembles the page, embeds the explanations of the classes present, writes
  `<base>.html`. Also `ink_census(strings, classes) -> (counts, unclassed)` - the FR-009 data,
  which `finish()` records in the manifest as `M["ink_classes"]` and `M["unclassed_ink"]`
  (element name + first 80 chars, capped at 20).
- `assets/page.css`, `assets/page.js` - read at write time and inlined (package data, so
  `tests/` can lint them as text and the page stays self-contained).

Ink that draws nothing - `<defs>`, `<pattern>`, `<clipPath>`, an empty string, a closing `</g>`,
the opening `<svg>` tag - is exempt from the census. The **not-highlighted list** (FR-002) is the
pseudo-class `NOT_HIGHLIGHTED = "-"`: the frame (background rect, title placard, scale bar) is
added with `cls="-"`, so it is RULED ON and accounted for, and the page wraps nothing for it. The
census reports only ink with no class at all - ink nobody has ruled on. A GM ruling that some
feature does not highlight is one `cls="-"` at its emit site plus a row in `classes.py`'s
`NOT_HIGHLIGHTED_RULINGS` (who, when, what) so the ruling is on the record.

### D3. The page (FR-003, FR-005, FR-006)

- The SVG is inlined at `width: 100%` inside a page with the map's name as `<h1>`; the browser's
  own zoom (ctrl+wheel) enlarges it - no pan/zoom of our own, none was asked for.
- Every classed primitive is wrapped: `<g class="f f-farmhouse">...</g>`. On load, the script
  indexes groups by class (a few hundred groups per class at most - a bead run is one `add()`
  string, so ~12,000 circles are one group).
- **Hover**: `pointerover` on the SVG walks `closest(".f")`, reads the class, and adds `on` to
  every group of that class; `pointerout` removes it. The highlight is a CSS rule on the group's
  descendants, not a filter: `.f.on, .f.on * { fill: <hl> !important; stroke: <hl-stroke>
  !important; }` - a flat rule the browser applies to a few hundred subtrees, never a restyle of
  the whole 175,000-element tree (research.md R2 measures this against SC-004). Highlight color:
  a saturated warm gold fill with a dark-amber stroke - legible against the parchment ground,
  the pale rice, the pine beans and the blue water alike (FR-003); recorded in research.md R2
  as a deviation-class rendering decision of the HTML target (the map's palette is the record;
  the highlight is a UI affordance and says so).
- **Labels**: a label is added with `cls=` of the feature it names (the kosatsuba's label gets
  `notice board`), so the two are one class and FR-006 falls out of FR-003. `label()` gains a
  `cls` parameter; the kosatsuba passes it.
- **Click**: opens a `<dialog>` with the class explanation: name; what; why here; the label in
  the words *historically accurate* / *deliberate deviation* / *guess*; the sibling paragraphs
  for siblings PRESENT on this map (the page embeds `siblings` only for keys in the map's own
  class set - US4 scenario 4); sources. Escape, the close button and a click on the backdrop
  close it (`<dialog>` gives the first two natively).
- The explanations are embedded as one JSON `<script type="application/json">` blob, filtered
  to the classes present.

### D4. Assigning classes at the emit sites (FR-004, FR-007)

One line per site, `with self.feature(...)` or `cls=`. The hamlet tier's sites:

| class | site |
|---|---|
| farmhouse / storage shed | `houses.py house()` (split the joined string into body and shed) |
| storage shed | `homestead_parts.py` farm sheds |
| byre | `shrines_wells/byres.py` |
| threshing yard, garden | `homestead_parts.py _draw_threshing_yard / _draw_garden` |
| privy, woodpile, manure heap, bathhouse, hen coop, household shrine | `farm_fixtures.py farm_fixture(kind)` - class from `kind` |
| persimmon | `farm_fixtures.py persimmon()` |
| homestead bamboo / shared bamboo grove | `homestead_parts.py bamboo_stand(role)` |
| windbreak / copse | `homestead_parts.py village_grove(role)` -> `_draw_grove` |
| woodland commons / scrub and rough grazing | `land/cover.py commons(role)` and the tree stands it draws via `woods.py` |
| marsh | `land/wet.py marsh()` |
| paddy + bund (split), millet/buckwheat/barley (from `p["crop"]`), bund beans, bund (junctions) | `fields/comb.py` - base fill `paddy`, paddies split, hem plots + furrows per crop, beads, junctions |
| field ditch | `fields/comb.py _comb_draw_ditches / _comb_source_channel`, the `_water` late block entries |
| stream, pond | `water_ways.py stream()`, `fields/features.py pond()` - via the `_water` entries' `cls` |
| village lane | `water_ways.py lane()` - every lane, the connector and spur included (spec: all ways are one feature); via `_ground` entries' `cls` |
| footbridge | wherever `bridges[].foot` is drawn (`hamletgen/frame.py stage_crossings` -> the settlement method it calls) |
| well | `shrines_wells/wells.py well()` |
| notice board | `structures/fixtures.py kosatsuba()` + its label |
| frame | `core.py _header()` background, `finish.py title()`, the scale bar |

Any site the census still reports on Inashiro after this pass is classed in the same task - the
census (`M["unclassed_ink"]`) is the worklist, and the gate check (D5) is what keeps it empty.

### D5. The gate check (FR-009)

`make new-check NAME=all_ink_is_classed ...` - a segment that fails when
`M["unclassed_ink"]` is non-empty, scoped to `meta.generated_by == "hamletgen"` (the spec: the
reference hamlet and the scripted hamlets; hand-authored tiers carry their vocabulary later). A
regression fixture in `pool/regressions/` with one unclassed snippet proves it fires (SC-006).

### D6. The pipeline (FR-011)

- `finish()` writes `<base>.html` right after the SVG and JSON, whenever it writes them (the
  write is cheap - a string pass; `DIAGRAM_SKIP_RENDER` skips only the raster).
- `render_cache._is_fresh` requires the `.html` beside the `.png`; `.gitignore` gains
  `pool/<tier>/*.html` for the four Mode B tiers.
- `pool_index.py` adds an "interactive" link beside the thumbnail when `<stem>.html` exists.
- The pool index itself stays where it is.

### D7. Verification in a browser (FR-012)

`tests/interactive/test_page_browser.py`: Playwright (Chromium, headless) opens
`pool/hamlets/inashiro.html` via `file://` (obtained through `gencache.gate_obtain` like every
other test that needs the reference map), and asserts SC-001 through SC-004 and US1-US5: zero
console errors, zero network requests, hover-all-of-kind and hover-none-of-others for every
class present and for the sibling pairs, label linkage, modal open/close, sibling text present
and absent-sibling text absent, timing. The test is skipped with a clear reason when Chromium is
not installed (so a container without it still runs `make quick`), and `setup-dev-env.sh`
installs Chromium so the gate always has it. A screenshot of the highlighted state is written to
the scratchpad for the GM's review.

## Project Structure

### Documentation (this feature)

```
specs/134-interactive-html-map/
├── gm-request.md   # the GM's words, verbatim
├── spec.md
├── plan.md         # this file
├── research.md     # R1 tagging design, R2 highlight mechanism + timing, R3 explanation sources, R4 accepted limitations
└── tasks.md
```

### Source Code (the diagram skill, `.claude/skills/diagram/`)

```
l7r/diagram/interactive/          # NEW: the HTML target
├── CLAUDE.md
├── __init__.py
├── classes.py                     # the vocabulary + explanations (FR-007, FR-008)
├── page.py                        # wrap, census, assemble, write
└── assets/page.css, page.js
l7r/diagram/settlement/core.py     # cls on the record streams; feature() context
l7r/diagram/settlement/finish.py   # class blocks in the splices; write_html; the census into M
l7r/diagram/settlement/...         # one line per emit site (D4)
l7r/diagram/check_village/segments_XX.py   # all_ink_is_classed
l7r/diagram/pipeline/render_cache.py, pool_index.py
tests/interactive/                 # registry, page, census, browser
tests/settlement/test_core_classes.py, tests/check_village/..., tests/pipeline/...
pool/regressions/<fixture>.json
research/README.md                 # pointer: the HTML map now exists; each entry is what a reader sees
```

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| A browser page in a repository whose constitution says Principle I is N/A here | the GM asked for the page (`gm-request.md`) | the template's own instruction is to reinstate the entry, not skip it; that is the GM's edit to the constitution and is proposed at the report, while this feature verifies the page in a headless browser (FR-012) so the substance of Principle I - the page is looked at, not assumed - holds now |
| One `add()` split into two (`house()`), changing SVG whitespace | the shed and the house are different classes (the GM: *"a farmhouse is not a shed"*) | tagging sub-ranges inside one string would need a second syntax for the same thing; a whitespace change draws no pixel and SC-005 proves it |
