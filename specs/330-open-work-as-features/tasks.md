# Tasks: Open work as features (feature 330)

**Input**: plan.md (D1-D7)

## Occasions

- none: nothing on any map is drawn or placed differently - the feature changes where open work is recorded

## Tasks

- [x] T01 `make speckit-todo`: `scripts/speckit-todo.py`, its tests red first in `tests/tooling/test_speckit_todo.py`, the make target and its line in the generated reference (D1, D2, FR-001, FR-002, FR-003, FR-009, SC-001)
      research: rendering
      verify: DONE. scripts/speckit-todo.py + make speckit-todo (in the generated reference); tests/tooling/test_speckit_todo.py red first (18 failed with no script), now 18 passed, including the real tree in under 2 s; on the real tree: 10 filed, 2 planned, 15 in progress, 220 closed
- [ ] T02 the gm-assistant check: every feature's spec and request searched for gm-assistant's own subjects, each hit read, any such feature deleted; the search and its result in `audit.md` (D4, FR-005, SC-005)
      research: rendering
- [ ] T03 settle every existing open feature: each status line rewritten only with its evidence in `audit.md` (done, superseded by, withdrawn by a cited ruling), the rest left open and listed for the GM (D3, FR-004, SC-002)
      research: rendering
- [ ] T04 file every `future-work/` entry: one claimed number per entry or named piece, a `spec.md` with the entry verbatim and its source, status Filed; an entry found done or disposed of by a cited ruling or later feature closed in `audit.md` instead (D5, FR-006, SC-003)
      research: rendering
- [ ] T05 re-aim every live pointer into `future-work/` at the feature its entry became, or drop it where the entry was closed (FR-007); `check-old-layout.py` refuses a new live mention, with its selftest (D6, FR-007, SC-004)
      research: rendering
- [ ] T06 the rules: the root `CLAUDE.md` and every doc that told a session to add to `future-work/` now say to file a feature and to ask `make speckit-todo` (D7, FR-008)
      research: rendering
- [ ] T07 `future-work/` deleted; `make speckit-todo` run before and after, both outputs and the spot check of ten listed and ten unlisted features recorded in `audit.md` (FR-007, SC-002, SC-003)
      research: rendering
- [ ] T08 `make done` green, then the stop-work procedure (VI, XIII)
      research: rendering
