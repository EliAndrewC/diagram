# Plan - 207 The incremental gate, and content as data

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI**: FR-014's fixture proves each failure fires; FR-015 measures rather than estimates.
- **X**: new code under `l7r/diagram/ci/` (measured, 100% owed); the content loaders are a few lines
  each; no file past 1,000 lines.
- **XII**: tooling feature; the one research question (what a tsubo-style content edit should cost)
  was answered by the GM in the request.
- **XIII**: a baseline on unmodified code is the full gate itself; the content moves are proved
  byte-identical (FR-008) before the gate work starts.
- **XVI**: spec-fidelity before code.
- **Route**: engine Python changes -> GATED (LOCAL-GATED); the first full gate with contexts is the
  baseline the incremental runs are measured against.

## Design

### Content as data (do first, land as one delta with the gate work)

- `interactive/assets/glossary.json`, `siblings.json`, `place.json`; loaders in the three modules.
- `classes/_base.py`: `parse_explanation` accepts `Label:`, `Sources:` (comma-separated keys),
  `Entry:`; `Kind.feature()` reads them; each `classes/*.py` class loses three attributes and gains
  three docstring lines (a scripted, asserted rewrite over 51 classes).
- `tools/placement_stages_notes.json`, `pipeline/pool_index.css`.
- `scripts/gate-stamp.py` `AREAS["page"]` -> `assets/*`; `render_cache.engine_fingerprint` hashes every
  file under `interactive/assets/`; `test_measured_surface.py` updated.

### The incremental gate

- `l7r/diagram/ci/incremental.py`: the planner - `manifest(root)`, `changed(baseline, current)`,
  `select(coverage_db, changed, collected)`, `prune(db_copy, contexts, files)`, `decide(...)` returning
  `full`/`incremental` with the reason; a `plan` command writes the selection file and prints the mode;
  a `merge` command prunes a copy of the baseline and combines; `save-baseline` copies `.coverage` and
  the manifest into `<git-dir>/gate-baseline/`.
- `l7r/diagram/ci/selection.py`: the pytest plugin (`-p l7r.diagram.ci.selection`), reads
  `L7R_GATE_SELECT`, deselects everything outside the keep set that the baseline knew, writes the
  collected node ids beside it.
- Makefile `test`: `--cov-context=test` always under `COV_FLOORS`; before pytest, `ci incremental plan`
  sets the mode; after a green run in incremental mode, `ci incremental merge` before the floors; after
  a green FULL floor phase, `ci incremental save-baseline`. `done` records `mode` and `selected`.
- `scripts/_gatecost.py` / `_ratchet.py`: `done` medians over full-mode entries; `check-run-plausible.py`
  takes the mode.
- Tests: `tests/tooling/ci/test_incremental.py` (pure functions over synthetic sqlite data) and
  `tests/tooling/test_incremental_gate.py` (the fixture project, `tooling` marker).
