# Feature 188 - the page check, and the tweak lane

**Status**: DRAFT - awaiting `spec-fidelity` (constitution XVI).
**Request**: [`request.md`](request.md) - the GM's words verbatim, three messages
**Predecessors**: feature 181 FR-010 (made the page's assets engine content for the gate key and the
route - the change this feature reverses, at the GM's clarification), 187 (the assets in the RENDER
fingerprint - kept), 174 (a plain `make done` is the full suite with the 100% floor - untouched for
engine code)

## Summary

The GM's clarification: a stylesheet change must make the pages regenerate when a clone lands on main,
and must NOT make every test re-run. Feature 187 already does the first. This feature undoes the second
- the assets leave the gate key and the route - and puts ONE check in its place, the version the GM
approved: a delta that touches the page's assets owes a green `make page-check` (the interactive unit
tests plus the browser test, about a minute) before it can push, refused exactly as an engine delta is
refused today without a green `make done`.

The same path rule is the **tweak lane**: an asset-only or docs-only delta needs no spec-kit feature,
no fidelity review and no task file - the tooling already exempts it once the assets are not engine
content, and the written rule says so. And `make tick` ticks a task from the command line, which removes
a class of bookkeeping round trips the GM measured.

## Functional requirements

### The assets leave the gate key and the route (FR-001 to FR-003)

- **FR-001** `ci/delta._ENGINE_DIRS` returns to `("l7r/", (".py",))`: a `.js`/`.css` change is not engine
  code for the ROUTE, so an asset-only delta is DIRECT and dispatches nothing. `delta.is_page_asset(path)`
  is added: true for a `.js` or `.css` under `l7r/diagram/interactive/assets/`.
- **FR-002** `scripts/gate-stamp.py`'s `AREAS["diagram"]` returns to `("*.py",)`, so an asset edit does not
  re-open `make done`'s short-circuit or demand a full run at push. A new area `page` covers
  `.claude/skills/diagram/l7r/diagram/interactive/assets` with `("*.js", "*.css")`.
- **FR-003** The gate's own short-circuit and record (`ci verified-done`, the run-log's `engine_key`) key
  on `delta.engine_key`, which follows `_ENGINE_DIRS`; nothing else moves. The render fingerprint
  (feature 187) is untouched: it is what makes the pages regenerate on landing, which is the half the GM
  meant.

### The page check (FR-004 to FR-006)

- **FR-004** A new target `make page-check` runs `tests/interactive/` and
  `tests/full/interactive/test_page_browser.py` whole, `-n auto`, `--no-cov`, and on success writes the
  `page` stamp (`gate-stamp.py --write page`) and records `green-local page-check`. About a minute
  (measured today: the browser file 20 to 35 s, the interactive unit files a few seconds). No coverage
  floor: a CSS or JavaScript change cannot change the coverage of any Python module.
- **FR-005** `make done` ALSO writes the `page` stamp on success: a full gate runs those same tests, so a
  green gate is a green page check. Otherwise an engine delta that also touched an asset would owe two
  runs for one proof.
- **FR-006** `gate-stamp.py --check` at push time refuses a delta touching the `page` area without a
  stamp matching the assets' current bytes, naming `make page-check` as the gate that stamps it (today's
  message names `make done` for `diagram` and `make hooks-test` for `hooks`; the refusal's "Python" wording
  becomes "code"). `scripts/test-gate-stamp.sh` gains the cases: an asset edit with no page stamp is
  refused and names `make page-check`; a matching stamp admits it; a stale stamp refuses; an asset edit
  demands NO diagram stamp.

### The tweak lane (FR-007 to FR-008)

- **FR-007** With FR-001 and FR-002 in place the tooling already treats an asset-only or docs-only delta
  as DIRECT with no spec-kit feature demanded (`feature-complete` applies to the GATED route), no review
  gate (it fires only on a `specs/` directory in the delta) and no task file; nothing in the tooling
  changes for this - the requirement is that a test PROVES it: an asset-only delta routes DIRECT
  (`test_delta.py`), and the `page` stamp is the only thing it owes (`test-gate-stamp.sh`).
- **FR-008** The written rule says so. Root `CLAUDE.md`: the "EXCEPTION - diagram ENGINE code always has
  a spec-kit feature" bullet, the route bullet under the stop-work procedure, and the "Docs-only diffs
  skip the gate" bullet all currently say the assets are engine content (feature 181's wording); each
  is corrected to: engine code is `l7r/**/*.py` outside `ci/` and the pool generators and manifests;
  the page's assets are a TWEAK - they owe a green `make page-check`, no spec-kit feature, no review, no
  tasks; docs owe nothing. `docs/session-clones.md:30` likewise. The skill `CLAUDE.md` command table
  gains `make page-check` and `make tick`. `interactive/CLAUDE.md` gains one line under "Verifying".

### `make tick` (FR-009 to FR-010)

- **FR-009** `make tick F=<feature> T=<task> NOTE="<verify text>" [BOXES=1]` in the skill Makefile runs
  `scripts/tick-task.py`: `F` is a spec number or directory name (`188`, or
  `188-page-check-and-the-tweak-lane`); it finds `- [ ] <T> ` in that spec's `tasks.md`, ticks it,
  replaces the task's `verify:` text with `DONE. <NOTE>`, and with `BOXES=1` ticks the three research
  boxes. It REFUSES, with the reason, when the task is missing, already ticked, or the note is empty, and
  it prints how many tasks remain open. It never writes the file on a refusal.
- **FR-010** `tests/tooling/test_tick_task.py` proves each behavior and each refusal on a fixture
  `tasks.md`, in the quick tier (it calls functions on files, like `test_file_scale.py`). `scripts/*.py`
  is the `hooks` stamp area, so the push owes a green `make hooks-test`, which is the existing rule.

### Tests that move (FR-011)

- **FR-011** `tests/tooling/ci/test_delta.py`'s feature-181 test (assets are engine) inverts: the two
  assets are NOT engine, `is_page_asset` is true for them and false for a `.txt` beside them and for a
  `.css` elsewhere. `tests/tooling/test_measured_surface.py`'s "two definitions both see the assets" test
  becomes: the `page` area sees exactly the two assets, the `diagram` area sees no asset, and
  `is_page_asset` agrees with the `page` area.

### What this feature does not do

- **FR-012** It does not change what `make done` runs for an engine delta (feature 174's full suite and
  100% floor stand), nor the render fingerprint (187), nor any page content or map.
- **FR-013** It does not put prose-only edits to engine Python (a class's explanation string in
  `classes.py`) in the tweak lane. The gate key is a docstring-stripped AST, and a string constant IS
  part of that AST, so the tooling cannot tell a prose edit from a behavior edit today. Recorded as D4
  so it is a decision the GM can reopen, not an omission.

## Decisions Recorded

- **D1 - what `page-check` runs.** The interactive unit tests (`tests/interactive/`) and the browser test
  are the only tests that read the assets or the page they are inlined into; every other test's outcome
  is independent of them by construction. Declined: running `tests/full/interactive/` (it holds only the
  browser test today), and running with coverage (nothing measurable can move).
- **D2 - one stamp, two writers.** `make done` writes the `page` stamp as well as `diagram`, because its
  suite includes the page tests. The alternative - a second run for an engine delta that also touched
  an asset - spends a minute proving what the nine minutes already proved.
- **D3 - the tweak lane is decided by PATH, the way the route is.** The tooling has one notion of "engine
  code", `delta.is_engine`; a tweak is a delta with none. No new classifier, no flag, no marker in a
  commit message - a rule a session could misapply is not a lane.
- **D4 - prose in `classes.py` stays engine code, for now.** See FR-013. The honest way to admit it would
  be a semantic key that hashes code with string constants blanked, which changes what `gate-stamp`'s
  `semantic_bytes` means for every record and is a feature of its own. Cost today: rewording a modal's
  explanation costs the full gate.
- **D5 - `make tick` refuses rather than guesses.** A task it cannot find, or one already ticked, is a
  refusal with the reason; the session's own bookkeeping errors this session (two regexes that matched
  nothing and wrote nothing, one heredoc that truncated a file) are exactly what a checked, single-purpose
  tool prevents.
