# Tasks: Open work as features (feature 330)

**Input**: plan.md (D1-D7)

## Occasions

- none: nothing on any map is drawn or placed differently - the feature changes where open work is recorded

## Tasks

- [x] T01 `make speckit-todo`: `scripts/speckit-todo.py`, its tests red first in `tests/tooling/test_speckit_todo.py`, the make target and its line in the generated reference (D1, D2, FR-001, FR-002, FR-003, FR-009, SC-001)
      research: rendering
      verify: DONE. scripts/speckit-todo.py + make speckit-todo (in the generated reference); tests/tooling/test_speckit_todo.py red first (18 failed with no script), now 18 passed, including the real tree in under 2 s; on the real tree: 10 filed, 2 planned, 15 in progress, 220 closed
- [x] T02 the gm-assistant check: every feature's spec and request searched for gm-assistant's own subjects, each hit read, any such feature deleted; the search and its result in `audit.md` (D4, FR-005, SC-005)
      research: rendering
      verify: DONE. audit.md A: every feature's spec, request and gm-request searched for gm-assistant subjects; 4 directories flagged (119, 127, 130, 131), each read - all diagram work; none deleted
- [x] T03 settle every existing open feature: each status line rewritten only with its evidence in `audit.md` (done, superseded by, withdrawn by a cited ruling), the rest left open and listed for the GM (D3, FR-004, SC-002)
      research: rendering
      verify: DONE. 27 open features settled by three independent passes: 19 Done and 3 Withdrawn, each status line carrying its evidence (settle.py); 111, 121, 312, 325 left open with what remains and what the GM must decide (audit.md C); speckit-todo now 39 filed, 3 in progress, 242 closed
- [x] T04 file every `future-work/` entry: one claimed number per entry or named piece, a `spec.md` with the entry verbatim and its source, status Filed; an entry found done or disposed of by a cited ruling or later feature closed in `audit.md` instead (D5, FR-006, SC-003)
      research: rendering
      verify: DONE. 37 entries checked (37 FILE, 0 DONE, 0 DISPOSED, audit.md B); 37 features filed, 331-367, each with the entry verbatim and its source; the 275 entry under its own number (350) naming 275 as history; filed.json maps entry -> feature
- [x] T05 re-aim every live pointer into `future-work/` at the feature its entry became, or drop it where the entry was closed (FR-007); `check-old-layout.py` refuses a new live mention, with its selftest (D6, FR-007, SC-004)
      research: rendering
      verify: DONE. repoint.py: 78 live pointers re-aimed (live entries name their feature: 342, 344, 350, 351, 354, 356, 357, 358, 365, 332; entries closed before this feature say so, git history); the exhibit's manifest and frame text, two test fixtures by hand; no live mention left outside the directory itself; check-old-layout.py refuses a new one, its selftest case red without the rule
- [ ] T06 the rules: the root `CLAUDE.md` and every doc that told a session to add to `future-work/` now say to file a feature and to ask `make speckit-todo` (D7, FR-008)
      research: rendering
- [ ] T07 `future-work/` deleted; `make speckit-todo` run before and after, both outputs and the spot check of ten listed and ten unlisted features recorded in `audit.md` (FR-007, SC-002, SC-003)
      research: rendering
- [ ] T08 `make done` green, then the stop-work procedure (VI, XIII)
      research: rendering
