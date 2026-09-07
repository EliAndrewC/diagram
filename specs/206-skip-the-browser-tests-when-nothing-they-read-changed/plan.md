# Plan - 206 Skip the browser tests when nothing they read changed

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **VI**: the skip is proved to fire once (SC-002) and the tooling tests prove the wiring and the key.
- **X**: no engine code; `gate-stamp.py` and the Makefile are guard files, so each edit carries the
  guard-edit marker with its reason in the diff; 100% coverage holds (nothing under `l7r/` changes).
- **XIII**: the floor cannot be loosened by a skip (R3); every other phase of the gate is unchanged.
- **XVI**: spec-fidelity before code.
- **Route**: Makefile + scripts + tests + docs -> DIRECT; `gate-stamp.py` is a guard script, so the push
  demands a green `make hooks-test`.

## Design

- `scripts/gate-stamp.py`: `AREAS["browser"]` rooted at `.claude/skills/diagram` with patterns
  `l7r/diagram/interactive/*.py`, `l7r/diagram/interactive/assets/*`, `tests/full/interactive/page_browser/*.py`,
  `research/*.html`; in `RAW_AREAS`. `_excluded` takes the area NAME (two areas now share a root, and the
  `diagram` area's `tests/` exclusion must not reach the browser area). `_salt(area)` folds the Playwright
  version and Chromium build into the browser hash. `check()` skips `SKIP_ONLY_AREAS = {"browser"}`.
  `write_stamp` takes a `root` so a test can drive it in a fixture repository.
- Makefile: `BROWSER_SKIP` (empty when the stamp is stale; else the ignore flag; no override) on the
  `test` recipe's pytest line, with one printed line when it skips; `page-check` writes `browser` after
  `page`; `done`'s phases-run exit writes `browser` only when `BROWSER_SKIP` was empty.
- Tests: `tests/tooling/test_browser_skip.py` (FR-006), in `test_page_check.py`'s style for the recipe text
  and a fixture git repository for the key; `scripts/test-gate-stamp.sh` unchanged (the shell suite covers
  the existing areas; the new area's behavior is proved in Python).
- Docs: the four places FR-007 names.
