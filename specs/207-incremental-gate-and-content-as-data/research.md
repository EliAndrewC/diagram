# Research - 207 The incremental gate, and content as data

Tooling research, nothing physical. Measured in the clone on 2026-09-07 unless dated otherwise.

## R1. Why `make done` costs ten minutes, and what it can and cannot skip

The run log since 2026-09-06 (25 green `done` runs): median 559 s; roll cache warm 492 s (4 runs),
cold 610 s (6). Feature 205's run: 589 s, cold. The phases of that run: static/format/typecheck ~2 s;
the reference roll, cache MISS, ~36 s; hooks-test 0 s (stamp fresh); the pytest suite 424 s (3,034
tests, the pool rolls inside `tests/gate/` fixtures at ~40 s of setup each, seeds 41-44); the hamlet
floor plus stamps and the ratchet ~127 s.

The gate has TWO settings and nothing between: `already verified` in seconds when the docstring-stripped
AST of every engine `.py` plus the pool generators and manifests matches the last green run
(`scripts/gate-stamp.py` `semantic_bytes`); otherwise the whole suite. Feature 174 (GM 2026-08-31)
made the whole suite mandatory because the 100% floor is measured over whatever ran, and a deselected
test takes its coverage with it. `make quick` selects by change (pytest-testmon, feature 135) and is
the only selective runner; the gate never selects.

The glossary edit (feature 205) also CHILLED the roll cache: `gencache.key_for` hashes the top level of
every module a roll imports, and `page.py` imports `glossary.py` while writing the map's page, so one
definition invalidated every cached roll (the 120 s warm/cold gap).

## R2. What content lives in code - the census

THE CRITERION (spec FR-005a, after round 1 of the review): prose a reader sees, or a record kept for a
reader, is content and moves to data; data the engine executes on is code and stays. Size is not a
criterion - the first pass used a 1.5 KB threshold and missed five short phrases. The census: every
module-level constant under `l7r/` holding a string of 16+ characters with a space in it (regexes and
markup excluded), and every class attribute of the registry; first the rows the threshold found:

| module | prose bytes | consumer | verdict |
|---|---|---|---|
| `interactive/glossary.py` `GLOSSARY` | 3,722 | `page.glossary_for`, one test | MOVE - page content |
| `interactive/classes/siblings.py` `_PAIRS` (+2 shared texts) | 10,098 | `classes/__init__.py` via `install_siblings` | MOVE - page content (a record, not rendered since 2026-08-28) |
| `interactive/classes/*.py` the `label`, `sources`, `entry` attributes | scattered | `Kind.feature()` | MOVE INTO THE DOCSTRING - the explanation's own label and research pointer belong with the explanation (feature 189 already exempted the docstring) |
| `interactive/place.py` `KINDS`, `CROPS`, `_CROP_LEAD`, `CROP_SENTENCES`, `COLLISIONS`, `BASIS`, `ENTRY` | 2,672 | `place.py`'s sentence builders | MOVE - page content; `KINDS` interpolates three demographic constants, so the data carries `{HAMLETS_PER_DOMAIN}`-style fields formatted at load |
| `tools/placement_stages.py` `NOTES` | 11,202 | the placement-stages diagnostic page | MOVE - prose of a tool's report |
| `pipeline/pool_index.py` `_CSS` | 1,142 | the pool index page | MOVE - a stylesheet, to a `.css` file |
| `overlap/taxonomy.py` the exemption rows | 15,602 | the overlap checks | KEEP - the engine EXECUTES these rows; an edit must run the gate |

Then the rows the criterion adds, all in the page package:

| constant | bytes | consumer | verdict |
|---|---|---|---|
| `page.py` `CAVEAT_LEAD` ("On the drawing: "), `REFERENCES_LEAD` (the line above the references list) | 141 | the page | MOVE - `assets/page-text.json` |
| `classes/_base.py` `_LABEL_WORDS` (the four label phrases), `CONVENTION_LEAD` ("Note: ") | ~90 | `label_phrase`, `lead_sentence` | MOVE - `page-text.json` |
| `classes/_base.py` `NOT_HIGHLIGHTED_RULINGS`, `NOT_HIGHLIGHTED_OVERTURNED` | 468 | the ink census tests; never rendered | MOVE - `page-text.json`; a record of the GM's rulings, like the sibling texts |
| `classes/*.py` `name`, `covers` | scattered | `page.explanations` (`name` is the modal's heading); `covers` is documentation | MOVE - docstring tags `Name:`, `Covers:` |
| `place.py` `BASIS_LEAD` ("What this rests on: ") | 20 | the place card | MOVE - with the rest of `place.py`'s content into `place.json` |
| `pipeline/pool_index.py` `TIER_SECTIONS` (the section headings), `TREE_BANNERS` (the two trees' banner prose) | 432 | the pool index page | MOVE - `pipeline/pool_index_text.json`, beside the stylesheet |
| `page.py` `HIT_REGIONS`, `HIT_FROM_MARKS`; `place.py` `PLACE_KEYS`, `CROPS`' keys | - | the writer: which manifest keys become hit regions, which notes keys the card reads | KEEP - keys the page executes on (the crop WORDS move with `place.json`) |
| `notes.py`, `page.py`, `sources.py`, `tags.py` regexes and markup templates | - | the parsers and the writer | KEEP - code |
| `overlap/taxonomy.py` | 15,602 | the checks | KEEP - executed (FR-007) |

Every other string constant in the engine is a message in code (an error text, a log line) or a key.

## R3. Where a content file must be seen, so it is not seen as engine

Path patterns outside the walk (the feature-161 lesson): every place the page's assets are enumerated.

- `scripts/gate-stamp.py` `AREAS["page"]` = `("assets/*.js", "assets/*.css", "classes/*.py")` - THE
  definition of a page asset; `tests/tooling/test_measured_surface.py` reads it. Becomes `assets/*`.
- `AREAS["browser"]` already carries `l7r/diagram/interactive/assets/*`.
- `l7r/diagram/pipeline/render_cache.py` `engine_fingerprint`: `is_asset = name.endswith((".js", ".css"))`
  - the render fingerprint that regenerates the pages on landing (feature 187). Becomes every file in
  `interactive/assets/`.
- `l7r/diagram/ci/delta.py` `_ENGINE_DIRS`: `l7r/**/*.py` only - a `.json` under `l7r/` is already
  DIRECT. Nothing to change; a test pins it.
- `l7r/diagram/pipeline/gencache.py` `record()`: a `.json` READ is not recorded as a dependency
  (`OUTPUT_SUFFIXES`), so a content file never keys a roll and never chills the roll cache - which is
  the outcome wanted; the gen cache's OUTPUTS (a pool map's `.html`) regenerate through the render
  fingerprint, not through the gen cache, so no stale page is served.
- `make page-check` runs `tests/interactive` and the browser package: the glossary test, the registry
  tests and the place-card tests all live in `tests/interactive`, so a content edit is verified by
  exactly the target an asset edit owes. The tool's notes and the pool index's stylesheet are outside
  every stamp area: an edit to them owes nothing at push, like a docs edit; `make quick` runs
  `tests/tools/test_placement_stages.py` (the NOTES-to-STAGES roster check) and the pool-index test.

## R4. The incremental gate - what makes the merge exact

Coverage 7.15.2 records DYNAMIC CONTEXTS under this core (proved with a scratch package: contexts
`''`, `tests/t.py::test_a|run`, `tests/t.py::test_b|run`, one `line_bits` row each). pytest-cov 7.1.0's
`--cov-context=test` labels every test's `setup`, `run` and `teardown` phases `<nodeid>|<phase>`
(`pytest_cov/plugin.py` `TestContextPlugin`), under xdist too. The data file is sqlite:
`file(id, path)`, `context(id, context)`, `line_bits(file_id, context_id, numbits)`; the empty context
holds import-time execution (collection imports every test module, which imports the engine).

The argument, so nobody has to rediscover it. Baseline B = the coverage data of the last FULL green
run, with contexts, and the manifest of every engine `.py` (semantic id) and every file under `tests/`
(bytes) at that run. Current tree T. Changed set C = files whose id differs, plus added and removed
files. Kept set K = every test whose baseline context executed any engine file in C, plus every test in
a test module in C, plus every collected test the baseline never saw. Deleted set D = baseline tests
not collected now. Merged data = B with the contexts of K, D and `''` removed, combined with the fresh
run of K. Soundness: a test outside K executed no file in C at B, and the only way it could reach
changed code now is through a file that changed - which would be in C, and it executed that file, so
it is in K. Its execution is therefore identical (the suite is deterministic: fixed seeds, no clock),
and its baseline context is its true coverage. New files are reached only through changed files, so K
covers them fresh. `''` is re-measured because collection still imports everything.

Why FILE-level selection and not testmon's block level: the baseline's line numbers for a changed
file are meaningless after the edit, so every test that executed that file must re-run to rebuild its
coverage - block-level selection would keep stale line data for a file whose lines moved.

Why the baseline is the last FULL run and never a merged result (no chaining): a merged result is
exact only under determinism, and the one thing chaining adds is that a nondeterministic slip
compounds silently. With a fixed baseline the selection grows as changes accumulate since the last
full run, and a full run (a fallback, `FULL=1`, an idle run) resets it.

Fallbacks to a FULL run, each because file-level selection cannot see the dependency: no baseline;
any changed engine file that is not `.py` (a pool generator or manifest); any changed file under
`tests/` that is not a test module (`conftest.py`, `_scope.py`, a `_helper.py`, `fixtures/`); the tooling
hash moved (Makefile, pyproject, lockfiles, `scripts/`); more than 60% of the suite selected (the saving
is then under the cost of a second collection, and a full run refreshes the baseline).

## R5. The coverage core, measured

Python 3.14 + coverage 7.15.2: the default core is sys.monitoring. On the fixture project of
`tests/tooling/test_incremental_gate.py` (eight tests, one session fixture), the contexts recorded:

| core | serial | xdist `-n 2` |
|---|---|---|
| sysmon (default) | 4 of 8 - `''`, `fixture:built`, `test_dike[1]|run`, `test_shallow|run` | 6 of 8, with phases misattributed (`test_dike[4]|teardown`) |
| ctrace | 8 of 8 | 8 of 8 |

The sysmon core disables a line's event after its first hit (a performance optimization coverage makes
for plain line coverage), so a second context executing the same line records nothing. The first fix
pinned `COVERAGE_CORE=ctrace`; R6 measured what that costs. The second fix keeps sysmon and re-arms its
events: `sys.monitoring.restart_events()` at every context switch. Measured on the same fixture project,
per (context, file) line sets: sysmon-with-restart 12 rows, ctrace 12 rows, 0 differing - identical,
serially and under xdist. The cost model is one event per executed line per CONTEXT (first hit), against
the C tracer's one event per EXECUTION; the map rolls, which dominate the suite, execute their lines
millions of times and a few thousand distinct lines, so the difference is the whole of R6's 2.4x.

## R6. What the C tracer and the contexts cost a FULL run - measured

The pytest phase of the whole suite, 8 workers, this clone, no other recorded gate running in the window:

| run | core | contexts | pytest phase | whole gate |
|---|---|---|---|---|
| 2026-09-07 18:06 (feature 205, before this feature) | sysmon | none | 424 s (3,034 tests) | 589 s (cold roll cache) |
| 2026-09-07 20:15 (this feature, red on two unrelated tests) | ctrace | per test + per fixture | 964 s (3,079 tests) | 971 s |
| 2026-09-07 20:41 (red on one count) | ctrace | per test + per fixture | 1,026 s (3,088 tests) | 1,067 s |
| 2026-09-07 21:04 (GREEN, the first baseline) | ctrace | per test + per fixture | 1,099 s (3,089 tests) | 1,273 s |
| 2026-09-07 21:57 (GREEN, the baseline that ships) | **sysmon, events re-armed** | per test + per fixture | **497 s** (3,072 tests) | **664 s** |

So the contexts themselves cost a full run about 17% on the pytest phase (424 -> 497 s) and 13% on the gate (589 -> 664 s, both cold); under the C tracer a FULL run had cost about 2.4x what it did, and the T12 runs taken under it showed why
that was not acceptable: a polder-only edit ran 33 of 3,075 tests in 381 s (a saving), but a core-placer
edit ran 318 tests in 1,203 s - every map re-rolled under the slow tracer - which is TWICE the old full
gate. The fix is R5's second paragraph: keep the fast core and re-arm its events, which removes the
tracer penalty from both the full run and the rolls. The numbers under the fast core are T11/T12's
final entries in tasks.md.

The first green run's number and the baseline file's size (under the C tracer): tasks.md T11.

## R7. The three incremental runs under the C tracer (T12, first set), and two things they exposed

Each run: one harmless executable statement planted in one function (`_ = 0`), `make done`, the probe
removed. Baseline: the 21:04 full run (R6's third row, 3,092 tests).

| edit | selected | pytest phase | whole gate | note |
|---|---|---|---|---|
| `waterfields/polder.py` `s_on_side` (a polder-only function) | 33 of 3,075 (27 tests + 2 fixtures touched it) | 244 s | 381 s | the 33 include the polder gate tests, whose fixtures re-roll the polder maps - correct, the engine changed |
| `settlement/houses.py` `house` (the core placer, every roll executes it) | 318 of 3,075 (248 + 4 fixtures) | 1,034 s | 1,203 s | every map re-rolled under the C tracer: NO saving against the old 589 s gate |
| `tools/notes_census.py` `census` (a tool) | 11 of 3,075 | 11 s | 437 s | see below |

Two findings. (1) THE C TRACER MADE THE CORE CASE WORSE THAN THE OLD GATE - a change every roll executes
must re-roll every map, and the tracer's per-execution cost falls on exactly that; R5's second fix (the
fast core with re-armed events) is what this measurement forced. (2) THE FLOOR PHASE RE-ROLLS SUBJECTS
THE SELECTED TESTS DID NOT: `hamlet_floor.module_set` asks `rollcache.report_deps` for each fixed
subject, and when a subject's cache key has moved it rolls the subject itself (~40-60 s each, serially)
- on the polder run that is the 137 s outside pytest (the two polder subjects), and on the tools run
~390 s, because the preceding core run had OVERWRITTEN every subject's single cache slot with its probe's
roll, so restoring `houses.py` left every key stale (a measurement artifact of the probe sequence: a real
edit is not restored; the second set runs tools first). The polder case is real: the selected polder tests
roll the same specs under `hamlet()`'s subject string, and the floor rolls them again under `report:`'s -
feature 192's double-roll shape, on the incremental path. Not fixed here (D14).

## R8. The three incremental runs under the fast core (T12, second set) - the numbers that ship

Same three probes, tools first so no earlier probe's roll had overwritten a cache slot. Baseline: the
21:57 full run (R6's last row, 664 s cold; 3,072 tests). The old gate, for comparison: 589 s cold.

| edit | selected | pytest phase | whole gate | against the old full gate |
|---|---|---|---|---|
| `tools/notes_census.py` `census` (a tool no roll executes) | 11 of 3,072 | 9 s | **32 s** | 18x faster |
| `waterfields/polder.py` `s_on_side` (polder-only) | 33 of 3,072 (27 + 2 fixtures) | 79 s | **219 s** | 2.7x faster; ~140 s of it is the floor's second roll of the two polder subjects (D14) |
| `settlement/houses.py` `house` (the core placer, every roll executes it) | 318 of 3,072 (248 + 4 fixtures) | 419 s | **595 s** | parity: every map re-rolls, and the rolls ARE the cost |
| (a full run, `INCREMENTAL=0` or a fallback) | 3,072 | 497 s | 664 s | 13% slower than before the feature - the contexts' price |

So the gate's cost now follows the change's REACH rather than the suite's size: a leaf edit is a
half-minute, a subsystem edit a few minutes, and a core-placer edit costs what it always did, because a
change every map executes must re-roll every map and no selection can avoid that. The GM's motivating
case - feature 205's one glossary term - is not in this table at all: it is a content edit now (R2), and
owes `make page-check`, about a minute, with no gate.
