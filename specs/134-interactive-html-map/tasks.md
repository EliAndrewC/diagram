# Tasks: The Interactive HTML Map (feature 134)

**Input**: [spec.md](spec.md) (fidelity-reviewed, FAITHFUL in 3 rounds), [plan.md](plan.md),
[research.md](research.md). Single artifact: Inashiro (`make reference` / `make map`). Scope was
LOCKED to the reference hamlet (feature 132) for the whole feature; the pool obligations are in
"Owed at unlock" at the end. `[P]` = ran in parallel with its neighbors.

Timing: the GM's request 2026-08-27 ~23:00Z; implementation complete the same night (the numbers
below are measured, from the run-log and the browser).

## Phase 0 - baselines (constitution XIII, before the first edit)

- [x] T01 baseline `make done` (locked scope) on unmodified code: GREEN, 2,530 passed / 2 skipped, 138 s (run-log; a fresh clone so `hooks-test` ran). Taken in the CLONE before the first edit rather than in a detached worktree: the worktree attempt failed in `state.py` (a worktree's `.git` is a file) - that defect is fixed in this feature (Phase 4). PNG baseline hash of `pool/hamlets/inashiro.png` in main: `09e8d5ab40270e086abb6f20b834425bf12d2a3d7f0de8fcd5ceaffd31324af6` at `f4e817f2` (SC-005's "before")
      research: rendering
- [x] T02 `make reference` before the change: inside T01's 138 s (`reference` ~32 s per the locked profile); after: `make map` regenerates Inashiro in 39-41 s including the svg, json, html and png writes (three runs: 39.0 / 40.1 / 40.6 s)
      research: rendering

## Phase 1 - the class rides in a side list (D1)

- [x] T03 `settlement/core.py`: `ClsTag` (`str | Split | Parts | None`, in `interactive/tags.py`), `cls` on `add`/`add_wall`/`add_label`/`add_top`, parallel `*_cls` lists, `add_parts()` (a None piece stays unwrapped - the shared wrapper tags), the `feature()` context manager, `cls` on `_ground()`/`_water()` entries; the sheet tagged `"-"` in `_header()`; the `landuse.py` late-block placeholder aligned too
      research: rendering
- [x] T04 `settlement/finish.py`: class blocks built beside the string blocks in the three splices (ground, water, late water, the pond relocation); `body_cls` aligned with `body` and a RuntimeError when they drift; the SVG written exactly as before; `M["ink_classes"]`, `M["unclassed_ink"]`, `M["unregistered_classes"]` from the census; `write_html()`; `cls` on `label()`; the placard, name, scale bar and captions tagged `"-"`
      research: rendering
- [x] T05 [P] `tests/settlement/test_core_classes.py` (6 tests): streams stay aligned through every splice; `feature()` nesting and restore; explicit `cls` wins; `add_parts` joins byte-identically; the Split reaches the page; the drift refusal; the frame's ruling
      research: rendering
- [x] T06 `make map` -> PNG hash `09e8d5ab...` UNCHANGED (SC-005), re-checked after every phase (four regenerations); the SVG whitespace-normalized identical to main's (`svg normalized identical: True`, 16,379,653 bytes vs main's 16,379,741 - the 88 bytes are main's render-cache stamp line)
      research: rendering

## Phase 2 - the registry and the page (D2, D3)

- [x] T07 `l7r/diagram/interactive/classes.py`: `FeatureClass`, `CLASSES` (34 entries - the 33 FR-007 rows plus `field pond`, see T17), `NOT_HIGHLIGHTED`, `NOT_HIGHLIGHTED_RULINGS` (3 rulings); every explanation written FROM the research.md R3 entry with its label and its `SOURCES.md` keys (`not recorded` where the entry itself says so); 30 sibling pair texts, installed symmetrically
      research: physical  (the explanations state how a place was farmed and lived in - written FROM the record, each with its pointer)
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited
      note: the research pass is R3 of research.md - every class mapped to the existing entry it is written from; no new historical question was opened (R3: "no new historical research is opened by this feature"), so the source-reader box is ticked on the record's own verdicts (the entries cite READ / SUMMARY-ONLY per claim and the explanations repeat only what those entries assert); recorded and cited = the `entry` and `sources` fields of every class, and the spec's Decisions Recorded table (one row per class)
- [x] T08 [P] `interactive/page.py`: `wrap()` (str / Parts / Split), `ink_census()` (clipPath / pattern / defs contents exempt; capped list with the count kept), `unregistered_classes()`, `present_classes()`, `explanations()` (present classes, present siblings, a stub for an unregistered key), `render_page()` / `write_html()`; `assets/page.css` (the `:not([fill="none"])` rule - research.md R2), `assets/page.js` (group index, hover toggle, `<dialog>`, `window.l7rMap` for the test)
      research: rendering
- [x] T09 [P] `tests/interactive/test_classes.py` (85 tests): every spec class registered and nothing else; every entry complete; a guess says guess; siblings closed and symmetric; the GM's named distinctions written; house style
      research: rendering
- [x] T10 [P] `tests/interactive/test_page.py` (16 tests): wrap of each tag kind; the split copies; census exemptions, split-once, parts-by-piece, the cap; self-containment; present-only data; the `</script>` escape
      research: rendering
- [x] T11 `interactive/CLAUDE.md` index (+ a row in the skill's `CLAUDE.md` table); `requirements-dev.in` + `.txt` gain `playwright==1.62.0` (pip-compile); `setup-dev-env.sh` installs Chromium
      research: rendering

## Phase 3 - classing the hamlet's ink (D4)

- [x] T12 houses: `house()` as `add_parts` (farmhouse / storage shed - the shed rect is `g[1]`); `byres.py` -> byre
      research: rendering
- [x] T13 [P] homestead parts: threshing yard, garden, `bamboo_stand(role)` -> homestead bamboo / shared bamboo grove, `_draw_grove(cls=)` from `village_grove(role)` -> windbreak / copse (a water_mouth grove and the per-house yashikirin stay unclassed, so the census reports them when a map draws one - neither is in the vocabulary); `farm_fixtures.py` `FIXTURE_CLASS[kind]`; persimmon
      research: rendering
- [x] T14 [P] land: `commons(role)` -> woodland commons / scrub and rough grazing (pasture stays unclassed, not in the vocabulary); `marsh()` -> marsh; `woods.py` tree stands carry `cls` through the deferred canopy (`_pending_stands` is a 4-tuple now)
      research: rendering
- [x] T15 [P] fields: comb floor -> paddy; paddies `Split("paddy", "bund")`; bund junctions -> bund; beads -> bund beans; hem plots + furrows -> `p["crop"]`; ditches / source channel / `channel()` / `field_channel()` -> field ditch (as defaults on the drawing methods); the pond's feeder -> field ditch
      research: rendering
- [x] T16 [P] water and ways: `stream(cls="stream")`; `pond()` -> pond; `_lane_ink_at` -> village lane (all four strokes, connector included); `bridge()` -> footbridge; `well()` -> well; `kosatsuba()` + its caption -> notice board
      research: rendering
- [x] T17 `make map`; the census was the worklist: 21 unclassed sites after Phase 1, 3 after the sweep (the in-field pond), 0 after `field pond` was added as a class - the FR-007 table did not name it and Inashiro draws one, so it is a row in the spec now (siblings pond, paddy) for the GM to overrule by name. Final census on Inashiro: 31 classes present, 0 unclassed, 0 unregistered; PNG hash unchanged
      research: rendering

## Phase 4 - the gate check (D5) and the pipeline (D6)

- [x] T18 `make new-check NAME=all_ink_is_ruled_on` into `segments_08d_kosatsuba_and_paddy_basins.py` (the scaffolder needs an existing themed file): fails on non-empty `unclassed_ink` or `unregistered_classes`, scoped to `meta.generated_by == "hamletgen"`; test `test_all_ink_is_ruled_on_fires_and_passes` (fires on unruled ink, fires on an unregistered class, passes with `-` ink, silent on a hand-authored tier); regression fixture `pool/regressions/all_ink_is_ruled_on_fires_on_an_unruled_element.json` (Inashiro's real manifest with one unruled rect) proves it fires (SC-006)
      research: rendering
- [x] T19 [P] `render_cache._is_fresh` requires the `.html` (frozen exhibits exempt); `gencache.OUTPUT_SUFFIXES` carries `.html` so a cache hit restores the page; `.gitignore` the four Mode B tiers' `*.html`; `pool_index.py` links "interactive" beside the notes; `tests/pipeline/test_render_cache.py` extended
      research: rendering
- [x] T19b defects fixed where found (constitution XIV): (a) `reink_lane` wrote `d="M"` for a lane `hamletgen.ways` had retired by emptying its record - resvg ignored it, Chromium logged an error on every open; it now blanks the ink (Inashiro's SVG had two such paths, now none); (b) `ci/state.py` wrote under `.git/` as a directory, which a `git worktree` does not have (`.git` is a file) - the reason T01's detached-worktree baseline could not run; `_state_file()` follows the `gitdir:` pointer now
      research: rendering

## Phase 5 - verified in a browser (D7)

- [x] T20 `tests/interactive/test_page_browser.py` (Playwright, Chromium, skipped with reason when absent): the SYNTHETIC page (quick) - hover-all / hover-none-of-others for every class and sibling pair, a real pointer over the second farmhouse lights both, the not-highlighted sheet lights nothing, the label lights the notice board and the click on the label opens its modal, backdrop / close button / Escape, the bund's stroke copy keeps `fill: none` when highlighted; the REFERENCE HAMLET page (`rolls_map`, `tiers("hamlet")`) - every present class and sibling pair, modal text per class, zero console errors, zero network requests. 6 passed in 74 s (whole file, including the Inashiro roll). SC-004 measured: load 2.1 s (SC: < 5 s); highlight 0.2-2.3 ms of script time, worst `bund` at 627 groups (SC: < 100 ms); 1,777 groups over 31 classes
      research: rendering
- [x] T21 screenshots for the GM in the session scratchpad (`smoke-windbreak.png` - the belt lit gold; `smoke-modal.png` - the notice board's modal); the closing bookend: every explanation read on the rendered page against its research.md R3 entry - the 34 rows of the spec's Decisions Recorded table are generated from the registry, one per class, each with its label, its note and its entry. Entries found THINNER than R3 first claimed, and labeled accordingly in the registry: `fallow` (no dedicated entry - guess), `footbridge` (planking reasoned, not read - guess), `woodpile` / `manure heap` / `bathhouse` / `hen coop` / `persimmon` (presence read, place or size a guess - each note says which)
      research: physical  (the explanations state how a place was farmed and lived in - written FROM the record, each with its pointer)
      - [x] research pass  - [x] source-reader confirmed  - [x] recorded and cited
- [x] T22 docs: `dev/placement.md` (the KEEP-CLEAR CONTRACT now says a new glyph carries its class); `research/README.md` says the page exists and where the explanations are; `SKILL.md` "Render pipeline" + the tracking paragraph gain the `.html`; `settlement/CLAUDE.md` rows for `core.py` and `finish.py`; `tests/CLAUDE.md` row for `interactive/`; `interactive/CLAUDE.md`
      research: rendering
- [x] T23 `make quick` green after every batch; `make done` (locked scope) green before the push - see the run-log; regression check against T01: zero new failures, PNG hash unchanged
      research: rendering

## Phase 6 - the GM's follow-ups of 2026-08-28 (spec FR-013, `gm-request.md` "Follow-ups")

- [x] T26 **no page header** - the GM: *"we can get rid of the entire header, the one whose text reads ... Inashiro / Hover a feature ... / 1 px = 1 ft"*. `page.py` writes no `<header>`, the CSS for it is gone; `test_page.py` asserts no `<h1>` and no hint. Given ~2026-08-28T00:10Z, done ~00:20Z, ~10 min, runs: test-file x2
      research: rendering
- [x] T27 **zoom in and out** - the GM: *"zoom in significantly more than we are zoomed in now ... zoom out ... to a degree that the entire settlement is visible all within the browser viewport"*. A full-viewport stage; the map opens at the view the GM saw (fit to the viewport's width - the addendum fidelity review struck "fit as the initial view" as unrequested); fit-the-whole-map is the floor (`fit` button, `0`); 16x fit the ceiling (`MAX_ZOOM`, a recorded judgment: ~11x the opening view on Inashiro, a foot at ~9 screen px); wheel zooms about the pointer, `+`/`-` buttons and keys zoom about the center, drag pans, a drag is never a click. Implemented as a LAYOUT resize of the SVG, not a CSS transform (a transform rasterizes the whole scaled map as one layer - a ~28,000 px texture at 16x). Two browser tests (fit / floor / ceiling; wheel-about-pointer / drag-pans / drag-is-not-a-click). Given ~00:25Z, done ~01:30Z, ~65 min - LONGER THAN IT SHOULD HAVE BEEN: (a) more cycles than needed - two patch scripts failed on their own quoting (a heredoc carrying JS and markdown; the third attempt went through a file), each a round trip; (b) more complicated than expected - see T28, a crash that was NOT the zoom
      research: rendering
- [x] T28 **defect found by T27's test run, fixed where found (XIV)**: `test_reference_hamlet_page` crashed the tab (`Keyboard.press: Target crashed`) on the real 16 MB page. Bisected standalone (five CSS variants all survived; RSS per variant identical) to `dialog.showModal()`: a modal dialog makes the rest of the document INERT and Chromium re-styles all ~175,000 map elements on every open and close - measured 1.1 s and +50 MB per cycle, 31 cycles in the test, on a container with ~3.4 GB free (other sessions hold 12 GB). The dialog is now non-modal over the page's own shade: 0.3 s and +1 MB per cycle; Escape, the shade and the close button close it. It had passed before only because the machine had the headroom that day
      research: rendering

- [x] T29 **the wheel scrolls, it does not zoom** - the GM: *"I don't want scrolling to zoom - I still want scrolling to scroll."* A wheel turn pans the map by its own travel; zoom is the buttons and keys only; the browser test asserts the wheel leaves the zoom unchanged and moves the map by the delta
      research: rendering

- [x] T30 **scrolling stops at the map's edge** - the GM: *"We should be able to scroll to the edge of the map, but not beyond it."* Every move (wheel, drag, zoom) is clamped: a map larger than the viewport on an axis stops with its edge at the viewport's edge; a smaller one is centered. Browser test: forty wheel turns each way land the corners exactly on the viewport's corners
      research: rendering

- [x] T31 **the unlock sweep arrived with main's own unlock (133 T92, merged 2026-08-28)**: the unlocked gate ran the 4-seed cohort and `all_ink_is_ruled_on` fired on seeds 41-44 - exactly the FR-009 sweep the spec owed at unlock. Rolled each seed and read its census: `soy` (the palette's fourth dry crop, never rolled on Inashiro), and on seed 42 the in-field `field rock` and `grave island` glyphs. Three classes added to the registry, the spec table and the test, from the existing `research/fields.md` entries (the grave island labeled DEVIATION - the entry's own calibrated liberty); seeds 41-44 re-rolled: 0 unclassed, 0 unregistered. The unlocked gate: 3,854 passed in 20:51 before the fix, 1 failure (this)
      research: rendering

## Owed at unlock (spec SC-008, FR-009; plan "Performance bookends")

Not tasks of this feature - the spec (round-1 fidelity finding 5) holds the feature to the
reference hamlet - but obligations the unlock inherits, recorded here so `make scope-unlock`'s
sweep knows what to look for:

- `make maps` over the scripted hamlets: every `.html` written; `all_ink_is_ruled_on` green on each (a class the hamlet vocabulary does not name - a water_mouth grove, a pasture, a yashikirin - fails there and gets its registry row then); a second hamlet's page through `test_page_browser.py`'s reference-tier checks.
- the perf bookends `134-start` / `134-end` per the plan (the engine change is one list append per `add()` and the page write at `finish()`; the locked measurement is T02's 39-41 s `make map`).
- the town / city vocabulary is a later feature (spec Assumptions): those maps write their `.html` today with every unnamed feature unclassed, and the check does not run on them.
