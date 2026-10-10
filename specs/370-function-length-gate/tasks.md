# Tasks: a mechanical cap on function length, held at the gate (feature 370)

**Input**: plan.md (decisions D1-D8). No map changes, so no review check is owed.

## Occasions

- none: every split is behavior-preserving and the pool is rerolled and diffed against HEAD's manifests (plan D5); no glyph, placement or sheet changes

## Phase 1 - the cap and its checks (test first)

- [ ] T01 tests/tooling/test_function_cap.py: under the project config a 101-statement function fails and 100 passes; `check-function-cap.py` names it with both ways out, in a linted tree and in `scripts/`; every suppression case of D3 (SC-001, SC-004; FR-001, FR-002, FR-004, FR-008) - written and seen RED before T02
      research: rendering
      verify: make test-file FILE=tests/tooling/test_function_cap.py red, then green after T03
- [ ] T02 pyproject.toml: PLR0915 selected, `max-statements = 100` with the survey's reason beside it (D1; FR-001, FR-005)
      research: rendering
      verify: T01's config cases green; the comment states 131 of 1,209 and "second most common"
- [ ] T03 scripts/gates/check-function-cap.py with `--selftest` (D2, D3); first in `make static` and `make quick`, and before every push in sync-with-main.sh (FR-002, FR-004, FR-008)
      research: rendering
      verify: T01 green; --selftest; make hooks-test green (the push suite)

## Phase 2 - the twelve splits (D4), each proven by its module's tests, then make quick

- [ ] T05 settlement/homestead_parts/stands.py `village_grove` (190)
      research: rendering
      verify: make test-file on its tests; ruff PLR0915 silent on the module
- [ ] T06 hamletgen/homesteads/stages.py `_seat_households` (169)
      research: rendering
      verify: as T05
- [ ] T07 hamletgen/ways/touch.py `_touch_junctions` (144)
      research: rendering
      verify: as T05
- [ ] T08 settlement/finish.py `finish` (133)
      research: rendering
      verify: as T05
- [ ] T09 compound.py `emit_svg` (127)
      research: rendering
      verify: as T05; the Mode A sheets' SVGs byte-identical
- [ ] T10 hamletgen/hinterland/parcels.py `open_ground_patches` (118)
      research: rendering
      verify: as T05
- [ ] T11 settlement/land/cover.py `commons` (115)
      research: rendering
      verify: as T05
- [ ] T12 settlement/fields/paddy.py (106)
      research: rendering
      verify: as T05
- [ ] T13 compound_parts.py (105)
      research: rendering
      verify: as T09
- [ ] T14 hamletgen/ways/web.py `stage_web` (103)
      research: rendering
      verify: as T05
- [ ] T15 scripts/record/uncited.py (122) and scripts/record/claims.py (110)
      research: rendering
      verify: make test-file on their tests

## Phase 3 - the record, and the proof

- [ ] T16 constitution clause 12 amended, 2.28.0 -> 2.29.0, the deferred TODOs closed; plan template's clause-12 paragraph (D7; FR-006, SC-005)
      research: rendering
      verify: the clause names 100, ruff's count, the reasoned noqa and research.md R1
- [ ] T17 CLAUDE.md "the gate" row, docs/guards.md record (D8)
      research: rendering
      verify: read back
- [ ] T18 the pool rerolled, `git diff --stat HEAD -- pool/` empty (D5; SC-003)
      research: rendering
      verify: the diff is empty; the Mode A sheets regenerate identically
- [ ] T19 the claims re-check: claims-owed, a bundle per module, impl-drift, claims-checked (D6; FR-007, SC-006)
      research: rendering
      verify: make claims-owed names nothing this feature introduced
- [ ] T20 the whole project under the cap, the gate green, the perf bookends (SC-002)
      research: rendering
      verify: ruff over the five held trees reports no PLR0915; make done green; make perf LABEL=370-end, perf-report AGAINST=370-start
