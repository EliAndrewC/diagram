# Tasks: Unskill the repository (feature 329)

**Input**: plan.md (D1-D13), research.md (R1-R6)

## Occasions

- none: no map draws or places anything differently - the move changes where code lives, not what it draws

## Tasks

- [x] T01 the baseline: `make done` green before the move, its counts in research.md R6 (FR-010, SC-002)
      research: rendering
      verify: DONE. DONE. make done green before the move (459 s; 10,818 passed, 3 skipped, 2 xfailed; 38 guard suites); counts in research.md R6
- [x] T02 the move: `git mv` of every tracked path to the root; the Makefile, `.gitignore` and `CLAUDE.md` merged; `SKILL.md` to `docs/usage.md` (D1, D2, D4, FR-001, FR-002, FR-003)
      research: rendering
      verify: DONE. DONE. 13,333 pure renames in one commit; the root forwarder retired; .gitignore merged; the skill index folded into the root CLAUDE.md; SKILL.md -> docs/usage.md; .claude/skills/ holds only the speckit skills
- [x] T03 one config root: `pyproject.toml` at the root with the fence carried, `ruff.toml` gone; the equal-lists measurement in R3; the seeded-lint and pytest-rootdir tests (D3, FR-002a, SC-007)
      research: rendering
      verify: DONE. DONE. pyproject.toml at the root, ruff.toml gone, the fence in extend-exclude; ruff file lists before/after IDENTICAL (831, R3); tests/tooling/test_lint_scope.py (seeded engine error fails, specs ignored, testpaths and coverage source pinned)
- [x] T04 the sweep and the hand edits: every live pointer, the path constants, the depth arithmetic, the claims-index keys; CI definitions (D5, D13, FR-004, SC-001)
      research: rendering
      verify: DONE. DONE. sweep.py over every live file plus about 111 hand edits (path constants, depth arithmetic, escaped and split forms, engine walks under l7r/); claims-index keys stripped; CI definitions swept; check-old-layout finds 0 live lines
- [x] T05 the guards and the old-layout check: each guard re-pointed with a test on the new path; `check-old-layout.py` in lint and push with its selftest (D6, D7, FR-006, FR-007, SC-001)
      research: rendering
      verify: DONE. DONE. every guard on the new path, make hooks-test HOOKS_ALL=1 39 suites green; check-old-layout.py (literal, split and escaped forms; ledger line by line) in static and push with its selftest; three sweep-mangled patterns fixed; the gate-stamp area at the root with the root trees excluded (the same 399 files)
- [x] T06 the carry and the in-flight clone: `_layout_carry.sh` in sync-in and on the mirror, the dirty-clone notice, the roll-cache seed path; `test-sync-with-main.sh` cases; R5 (D8, D9, FR-008, FR-009, SC-004, SC-005)
      research: rendering
      verify: DONE. DONE. _layout_carry.sh in sync_in, mirror_refresh and the clone-sync hook, with selftest in the gate; merge.directoryRenames in sync_in and setup-dev-env.sh; test-sync-with-main case 15 red without the flag, green with (R5)
- [x] T07 the Markdown audit applied: `audit.md` with every member listed, each verdict carried out, the claims of a moved Mode A section renamed (D12, FR-012, SC-006)
      research: rendering
      verify: DONE. DONE. audit.md applied: 9 docs deleted with their facts carried, 8 moved, 5 created (research/downloads.md, record-checks.md, dev/ci.md, interactive-page.md, test-cost.md), the rest trimmed; departures recorded in audit.md 'Applied'; test_doc_links.py holds every live link
- [x] T08 the history note, the skill's explanation, the outside pointers: the root `CLAUDE.md` specs line, `dev/skill-boundary.md`, the memory entry; gm-assistant reported (D10, D11, FR-005, FR-011, SC-003, SC-005)
      research: rendering
      verify: DONE. DONE. the root CLAUDE.md names the move and how to read an old spec's path; docs/package-boundary.md rewritten as one package; the memory entry written; gm-assistant's docs/iteration-loop.md reported, not edited
- [x] T09 verification: `make hooks-test` and `make done` green from the root; counts against R6; Claude Code's skill list; the first gate in a second clone after the carry (FR-010, SC-002, SC-003, SC-004)
      research: rendering
      verify: DONE. DONE. make hooks-test HOOKS_ALL=1 39 suites green; make done GREEN 217 s, 10,824 passed (baseline 10,818); no diagram skill under .claude/skills/; the roll cache carried and HIT (R6)
