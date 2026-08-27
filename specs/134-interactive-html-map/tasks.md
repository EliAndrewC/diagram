# Tasks: The Interactive HTML Map (feature 134)

**Input**: [spec.md](spec.md) (fidelity-reviewed), [plan.md](plan.md), [research.md](research.md).
Single artifact: Inashiro (`make reference`). Scope is LOCKED to the reference hamlet (feature
132); every pool step below is marked "on unlock" and stays open until then. `[P]` = can run in
parallel with its neighbors.

## Phase 0 - baselines (constitution XIII, before the first edit)

- [ ] T01 baseline `make done` (locked scope) on unmodified code in a detached worktree; record the result and the time here. PNG baseline hash of `pool/hamlets/inashiro.png` in main: `09e8d5ab40270e086abb6f20b834425bf12d2a3d7f0de8fcd5ceaffd31324af6` at `f4e817f2` (SC-005's "before")
- [ ] T02 `make reference` time before the change (the one perf measurement the lock permits): __ s

## Phase 1 - the class rides in a side list (D1)

- [ ] T03 `settlement/core.py`: `ClsTag` (`str | Split | Parts | None`), `cls` on `add`/`add_wall`/`add_label`/`add_top`, parallel `*_cls` lists, `add_parts()`, the `feature()` context manager, `cls` on `_ground()`/`_water()` entries; NOT_HIGHLIGHTED = `"-"` on the frame in `_header()`
- [ ] T04 `settlement/finish.py`: class blocks built beside the string blocks in the three splices; the final `body_cls` aligned with `body`; the SVG written exactly as before; `M["ink_classes"]` + `M["unclassed_ink"]` from the census; `write_html()` call; `cls` on `label()`; the title placard and scale bar tagged `"-"`
- [ ] T05 [P] `tests/settlement/test_core_classes.py`: streams stay aligned through every splice (ground, water, late water, pond relocation); `feature()` nesting; explicit `cls` wins; `add_parts` joins byte-identically; `Split` recorded
- [ ] T06 `make reference` -> PNG hash unchanged (SC-005); whitespace-normalized SVG identical to the baseline's

## Phase 2 - the registry and the page (D2, D3)

- [ ] T07 `l7r/diagram/interactive/classes.py`: `FeatureClass`, `CLASSES` (one per FR-007 row), `NOT_HIGHLIGHTED`, `NOT_HIGHLIGHTED_RULINGS`; explanations written FROM the research.md R3 entries with their labels and `SOURCES.md` keys; sibling text per pair, symmetric
- [ ] T08 [P] `interactive/page.py`: `wrap()` (str / Parts / Split), `ink_census()`, `write_html()` embedding CSS, JS and the filtered explanation JSON; `assets/page.css`, `assets/page.js` (hover -> class toggle on the indexed groups; click -> `<dialog>`; Escape / close / backdrop)
- [ ] T09 [P] `tests/interactive/test_classes.py`: every class has name, what, why, one of three labels, a sources line; siblings symmetric and closed over `CLASSES`; every FR-007 key present (SC-007)
- [ ] T10 [P] `tests/interactive/test_page.py`: wrap of each tag kind; the split copies (fill-only / stroke-only); census exempts non-ink and `"-"`; the page is self-contained (no `http`, no `src=`/`href=` to the outside); embedded JSON holds only present classes and their present siblings
- [ ] T11 `interactive/CLAUDE.md` index; `requirements-dev.in` + `.txt` gain `playwright` (pip-compile); `setup-dev-env.sh` installs Chromium

## Phase 3 - classing the hamlet's ink (D4)

- [ ] T12 houses: `house()` as `add_parts` (farmhouse / storage shed); farm sheds -> storage shed; `byres.py` -> byre
- [ ] T13 [P] homestead parts: threshing yard, garden, `bamboo_stand(role)` -> homestead bamboo / shared bamboo grove, `village_grove(role)` -> windbreak / copse; `farm_fixtures.py` kind -> class; persimmon
- [ ] T14 [P] land: `commons(role)` -> woodland commons / scrub and rough grazing (and the tree stands it draws); `marsh()` -> marsh
- [ ] T15 [P] fields: comb base fill -> paddy; paddies `Split("paddy", "bund")`; bund junctions -> bund; beads -> bund beans; hem plots + furrows -> the crop; fallow; ditches / source channel -> field ditch
- [ ] T16 [P] water and ways: `stream()` -> stream; `pond()` -> pond; `lane()` -> village lane (all of them); footbridges -> footbridge; `well()` -> well; `kosatsuba()` + its label -> notice board
- [ ] T17 `make reference`; the census (`M["unclassed_ink"]`) is the worklist - class every remaining site until it is empty; PNG hash unchanged again

## Phase 4 - the gate check (D5) and the pipeline (D6)

- [ ] T18 `make new-check NAME=all_ink_is_ruled_on ...`: fails on non-empty `unclassed_ink`, scoped to `meta.generated_by == "hamletgen"`; regression fixture in `pool/regressions/` proves it fires; a `"-"`-tagged element does not (SC-006)
- [ ] T19 [P] `render_cache._is_fresh` requires the `.html`; `.gitignore` the four Mode B tiers' `*.html`; `pool_index.py` links "interactive"; tests in `tests/pipeline/`

## Phase 5 - verified in a browser (D7)

- [ ] T20 `tests/interactive/test_page_browser.py` (Playwright, Chromium, skipped with reason when absent): SC-001 zero console errors / network requests; US1-US3 hover-all / hover-none-of-others for every class and every sibling pair present; US4 click, modal text (name, label word, present siblings named, absent siblings not), Escape / close / backdrop; US5 label <-> notice board; SC-004 timing recorded here: highlight __ ms, load __ s
- [ ] T21 screenshot of a highlighted state to the scratchpad for the GM; the closing bookend: read every explanation on the rendered page against its research.md R3 entry; fill the spec's Decisions Recorded table one row per class; any entry found thinner than R3 claims is listed here
- [ ] T22 `dev/` docs: `dev/placement.md` (or the interactive CLAUDE.md) records where a new feature gets its class; `research/README.md` says the page exists; `SKILL.md` "Render pipeline" gains the `.html`
- [ ] T23 `make quick`, then `make done` (locked scope) green; `make reference` time after: __ s; regression check against T01

## On unlock (owed, not this feature's condition - spec SC-008, FR-009)

- [ ] T24 `make maps` over the scripted hamlets: every `.html` written; FR-009 green on each; a second hamlet's page through the browser test
- [ ] T25 perf bookends `134-start` / `134-end` taken at unlock per the plan
