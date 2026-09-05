# Tasks - feature 188

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

Every task is `research: rendering` - tooling, nothing physical behind it.

- [x] T01 FR-001/FR-003/FR-011: `ci/delta.py` - `_ENGINE_DIRS` back to `.py`; `test_delta.py` inverted
      research: rendering
      verify: DONE. `_ENGINE_DIRS` is `("l7r/", (".py",))` again with the GM quoted at the point of change; `test_delta.py` inverted - the two assets are not engine for the route, the page WRITER still is
- [x] T02 FR-002/FR-006/FR-011: `gate-stamp.py` - `diagram` back to `*.py`, new `page` area naming `make page-check`; `test-gate-stamp.sh` cases; `test_measured_surface.py`
      research: rendering
      verify: DONE. `diagram` back to `*.py`; `page` area over `interactive/assets` (`*.js`, `*.css`), named as THE definition; `check()` names `make page-check`; "Python" -> "code". `scripts/test-gate-stamp.sh`: an asset edit with no page stamp is refused naming make page-check and demanding no diagram stamp; a diagram stamp (the short-circuit) does not admit it; a matching page stamp does; a stale one refuses. Green
- [x] T03 FR-004/FR-005: `make page-check` (interactive tests + the browser test, no coverage, stamps `page`, records nothing else); `make done`'s phases-run exit stamps `page` too, the short-circuit does not
      research: rendering
      verify: DONE. `make page-check` runs `tests/interactive` + the browser file, `--no-cov`, writes the page stamp and nothing else; `make done` writes `page` beside `diagram` on the phases-run exit only (a GUARD_EDIT_OK note beside it says why the short-circuit does not); forwarded from the root Makefile. `tests/tooling/test_page_check.py` reads the recipe text and proves it. MEASURED: 26 s, 420 tests
- [x] T04 FR-009/FR-010: `scripts/tick-task.py` + `make tick`; `tests/tooling/test_tick_task.py`
      research: rendering
      verify: DONE. `scripts/tick-task.py` (refuses on a missing or ticked task or an empty note, ticks the boxes with --boxes, resolves a spec by number or name and refuses ambiguity, keeps the blank lines before a section heading) + `make tick`, whose NOTE travels in the environment because a backtick interpolated into the recipe ran as a command on the first real use; `tests/tooling/test_tick_task.py`, 9 tests. This very line was written by it
- [x] T05 FR-007/FR-008: the written rule - root `CLAUDE.md` x3, `docs/session-clones.md`, skill `CLAUDE.md` table, `interactive/CLAUDE.md`
      research: rendering
      verify: DONE. root `CLAUDE.md` x3, `docs/session-clones.md`, the skill `CLAUDE.md` table (page-check, tick), `interactive/CLAUDE.md` Verifying, and the root Makefile forwards the two targets; grep for feature 181 engine-content wording finds only the records
- [x] T06 `make done` green (this delta touches `ci/delta.py`, engine for coverage), `hooks-test` green, push; the answer to the GM with the measured cost of `make page-check`
      research: rendering
      verify: DONE. `make done` GREEN in 628 s: 2,963 passed, 22,576 statements 0 uncovered 100%, hamlet floor 100%; both `gate-green-diagram` and `gate-green-page` written by the phases-run exit at 19:41:13. `make page-check` MEASURED at 26 s for 420 tests. `PAIR_OK` given: tooling only, no drawn ink. Pushed
