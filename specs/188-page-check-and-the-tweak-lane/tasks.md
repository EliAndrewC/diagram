# Tasks - feature 188

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

Every task is `research: rendering` - tooling, nothing physical behind it.

- [ ] T01 FR-001/FR-003/FR-011: `ci/delta.py` - `_ENGINE_DIRS` back to `.py`; `is_page_asset()`; `test_delta.py` inverted
      research: rendering
      verify: an asset-only path is not engine and is a page asset; `make quick` clean
- [ ] T02 FR-002/FR-006/FR-011: `gate-stamp.py` - `diagram` back to `*.py`, new `page` area naming `make page-check`; `test-gate-stamp.sh` cases; `test_measured_surface.py`
      research: rendering
      verify: `scripts/test-gate-stamp.sh` green with the four new cases; `make hooks-test` green
- [ ] T03 FR-004/FR-005: `make page-check` (interactive tests + the browser test, no coverage, stamps `page`); `make done` stamps `page` too
      research: rendering
      verify: `make page-check` green in about a minute and writes `.git/gate-green-page`; `make done`'s success path writes it
- [ ] T04 FR-009/FR-010: `scripts/tick-task.py` + `make tick`; `tests/tooling/test_tick_task.py`
      research: rendering
      verify: the test file green; `make tick F=188 T=T04 NOTE=...` ticks this very task
- [ ] T05 FR-007/FR-008: the written rule - root `CLAUDE.md` x3, `docs/session-clones.md`, skill `CLAUDE.md` table, `interactive/CLAUDE.md`
      research: rendering
      verify: grep finds no statement that the assets are engine content for the gate or the route
- [ ] T06 `make done` green (this delta touches `ci/delta.py`, engine for coverage), `hooks-test` green, push; the answer to the GM with the measured cost of `make page-check`
      research: rendering
      verify: green gate; the push lands; `make page-check` timed
