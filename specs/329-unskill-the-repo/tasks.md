# Tasks: Unskill the repository (feature 329)

**Input**: plan.md (D1-D13), research.md (R1-R6)

## Occasions

- none: no map draws or places anything differently - the move changes where code lives, not what it draws

## Tasks

- [x] T01 the baseline: `make done` green before the move, its counts in research.md R6 (FR-010, SC-002)
      research: rendering
      verify: DONE. DONE. make done green before the move (459 s; 10,818 passed, 3 skipped, 2 xfailed; 38 guard suites); counts in research.md R6
- [ ] T02 the move: `git mv` of every tracked path to the root; the Makefile, `.gitignore` and `CLAUDE.md` merged; `SKILL.md` to `docs/usage.md` (D1, D2, D4, FR-001, FR-002, FR-003)
      research: rendering
- [ ] T03 one config root: `pyproject.toml` at the root with the fence carried, `ruff.toml` gone; the equal-lists measurement in R3; the seeded-lint and pytest-rootdir tests (D3, FR-002a, SC-007)
      research: rendering
- [ ] T04 the sweep and the hand edits: every live pointer, the path constants, the depth arithmetic, the claims-index keys; CI definitions (D5, D13, FR-004, SC-001)
      research: rendering
- [ ] T05 the guards and the old-layout check: each guard re-pointed with a test on the new path; `check-old-layout.py` in lint and push with its selftest (D6, D7, FR-006, FR-007, SC-001)
      research: rendering
- [ ] T06 the carry and the in-flight clone: `_layout_carry.sh` in sync-in and on the mirror, the dirty-clone notice, the roll-cache seed path; `test-sync-with-main.sh` cases; R5 (D8, D9, FR-008, FR-009, SC-004, SC-005)
      research: rendering
- [ ] T07 the Markdown audit applied: `audit.md` with every member listed, each verdict carried out, the claims of a moved Mode A section renamed (D12, FR-012, SC-006)
      research: rendering
- [ ] T08 the history note, the skill's explanation, the outside pointers: the root `CLAUDE.md` specs line, `dev/skill-boundary.md`, the memory entry; gm-assistant reported (D10, D11, FR-005, FR-011, SC-003, SC-005)
      research: rendering
- [ ] T09 verification: `make hooks-test` and `make done` green from the root; counts against R6; Claude Code's skill list; the first gate in a second clone after the carry (FR-010, SC-002, SC-003, SC-004)
      research: rendering
