# Tasks: a mechanical cap on function length, held at the gate (feature 370)

**Input**: plan.md (decisions D1-D8). No map changes, so no review check is owed.

## Occasions

- none: every split is behavior-preserving and the pool is rerolled and diffed against HEAD's manifests (plan D5); no glyph, placement or sheet changes

## Phase 1 - the cap and its checks (test first)

- [x] T01 tests/tooling/test_function_cap.py: under the project config a 101-statement function fails and 100 passes; `check-function-cap.py` names it with both ways out, in a linted tree and in `scripts/`; every suppression case of D3 (SC-001, SC-004; FR-001, FR-002, FR-004, FR-008) - written and seen RED before T02
      research: rendering
      verify: DONE. test_function_cap.py seen red (no check, no setting), 30 green after T02-T03
- [x] T02 pyproject.toml: PLR0915 selected, `max-statements = 100` with the survey's reason beside it (D1; FR-001, FR-005)
      research: rendering
      verify: DONE. max-statements 100 with the survey's 131 of 1,209 beside it; the config cases green
- [x] T03 scripts/gates/check-function-cap.py with `--selftest` (D2, D3); first in `make static` and `make quick`, and before every push in sync-with-main.sh (FR-002, FR-004, FR-008)
      research: rendering
      verify: DONE. check-function-cap.py selftest ok (also with HOME moved); first in static and quick; push suite 116 green

## Phase 2 - the twelve splits (D4), each proven by its module's tests, then make quick

- [x] T05 settlement/homestead_parts/stands.py `village_grove` (190)
      research: rendering
      verify: DONE. village_grove -> grove_fill.py's four parts; homestead_parts, woods, belt and grove_blocks tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T06 hamletgen/homesteads/stages.py `_seat_households` (169)
      research: rendering
      verify: DONE. _seat_households -> _seat_rank_rounds, _ground_push, _offer_seat; homesteads tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T07 hamletgen/ways/touch.py `_touch_junctions` (144)
      research: rendering
      verify: DONE. _touch_junctions -> _one_network; touch, matrix and clearance tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T08 settlement/finish.py `finish` (133)
      research: rendering
      verify: DONE. finish -> _record_scatter_frame, _water_block; finish and core tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T09 compound.py `emit_svg` (127)
      research: rendering
      verify: DONE. emit_svg -> _draw_buildings, _draw_walls_and_gates; compound and labels tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T10 hamletgen/hinterland/parcels.py `open_ground_patches` (118)
      research: rendering
      verify: DONE. open_ground_patches -> _patch_keepouts, _beyond_the_fields; woodland and hinterland tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T11 settlement/land/cover.py `commons` (115)
      research: rendering
      verify: DONE. commons -> _stock_woodland; woods and homestead tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T12 settlement/fields/paddy.py (106)
      research: rendering
      verify: DONE. water_field -> _wf_outline, _wf_feed; fields tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T13 compound_parts.py (105)
      research: rendering
      verify: DONE. _point_features -> _draw_point_parts; compound tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T14 hamletgen/ways/web.py `stage_web` (103)
      research: rendering
      verify: DONE. stage_web -> _web_cut_lines; web tests green (ruff PLR0915 silent; the pool identity is T18's)
- [x] T15 scripts/record/uncited.py (122) and scripts/record/claims.py (110)
      research: rendering
      verify: DONE. claims.py and uncited.py main -> _parser; their tests green; check-function-cap.py exits 0 over the project (ruff PLR0915 silent; the pool identity is T18's)

## Phase 3 - the record, and the proof

- [x] T16 constitution clause 12 amended, 2.28.0 -> 2.29.0, the deferred TODOs closed; plan template's clause-12 paragraph (D7; FR-006, SC-005)
      research: rendering
      verify: DONE. clause 12 names ruff's count, 100, the reasoned noqa on the def line and R1's 131 of 1,209; 2.28.0 -> 2.29.0 with the TODO closed; plan template's paragraph
- [x] T17 CLAUDE.md "the gate" row, docs/guards.md record (D8)
      research: rendering
      verify: DONE. CLAUDE.md gate row; docs/guards.md row beside the file cap, its stale 'still owed' line updated
- [x] T18 the pool rerolled, `git diff --stat HEAD -- pool/` empty (D5; SC-003)
      research: rendering
      verify: DONE. make maps SCOPE=all (5 hamlets) and make map on all 6 Mode A sheets: REGENERATED, git status -- pool/ empty: byte-identical to HEAD
- [ ] T19 the claims re-check: claims-owed, a bundle per module, impl-drift, claims-checked (D6; FR-007, SC-006)
      research: rendering
      verify: make claims-owed names nothing this feature introduced
- [ ] T20 the whole project under the cap, the gate green, the perf bookends (SC-002)
      research: rendering
      verify: ruff over the five held trees reports no PLR0915; make done green; make perf LABEL=370-end, perf-report AGAINST=370-start
