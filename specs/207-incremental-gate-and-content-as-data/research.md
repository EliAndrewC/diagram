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

Cost of contexts on the full run: to be measured on the first full run (`--cov-context=test` is the
only change to the pytest line). The baseline file's size: measured then.
