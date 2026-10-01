# Tasks - feature 294, rethinking the settlement review

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A-I, D1-D17; review CLEAR at round 3). Research: [`research.md`](research.md)
(R0-R3) and [`rules-recon.md`](rules-recon.md).
Order (plan): the trigger and the guards first, because every later engine task is verified under them; then the contracts;
then the rules, Mode B then Mode A, each engine fix on its reference artifact before the pool; then the ledger, the documents
and the tier experiment; then the landing.

## Occasions

This feature's own delta, declared under the rules it builds (plan D10). Lines are added as the rules land.

- none: B1 - the polder feed's channel record traces its drawn stub (settlement/fields/comb.py); nothing drawn moves, every element placed under rules already judged
- none: B10 - the nucleated placer refuses a layout whose lot found no seat for a part (settlement/rolling/fit.py), the rule `_bundle_side_fits` already held; households re-seat under rules already judged, and a fixture kind new to a map is detected and owes its glyph check
- placement-changed: copse - B9: the dooryard copse is filled to the ground's capacity and trimmed back to each homestead's wood, rolled within the part of the register's range the ground can hold (settlement/homestead_parts/wood_goal.py)
- none: B7 - a farmhouse is seated with its wall `TREAD_WALL_FT` (4 ft) clear of a way's tread edge, where the hair was 2 ft (settlement/houses.py); a margin tuned, the seating rule otherwise the one already judged
- placement-changed: irrigation ditch - B4: a delivery that would run beside another watercourse as its twin is not drawn; its plots take their water over the bund (waterfields/twins.py, comb.py)
- placement-changed: drainage ditch - B4: a field's drain that would run beside the brook as its twin joins it (hamletgen/sink.py)
- glyph-redrawn: copse - B5b: a grove's conifers are painted over its lesser crowns, and a lesser crown that would lie over an earlier conifer is not drawn (settlement/homestead_parts/groves.py) - the farm groves of Kashikawa and Mizuguchi drew 307 broadleaf over conifers

## Setup

- [x] T01 The baseline: `/tmp/base294` (detached worktree at the spec's HEAD) and the `294-start` bookend on unmodified code
      research: rendering
      verify: DONE. DONE. /tmp/base294 detached at 4a/HEAD before any edit; 294-start bookend on unmodified code: total 17.9 s, median 4.2 s, worst 5.8 s (dev/perf-log/20261001T151220Z-294-start-diagram-review.json)

## The trigger and the guards (D, E, F)

- [x] T02 [US3] [US4] `scripts/_review_owed.py` answers occasions (detected: maps/sheets new to the pool, elements new to a map or sheet; declared: the `## Occasions` section), `--units`, `--check-declared`; `tests/tooling/test_review_owed.py` rewritten over git fixtures (D1-D3)
      research: rendering
      verify: DONE. DONE. _review_owed.py: Unit(check, subject, on, occasion), detected (maps/sheets new to the pool; ink_classes / data-kind new to a map or sheet, new-map elements only when new to the pool legend; a generated sheet's base from the mirror) and declared (## Occasions: glyph-redrawn, placement-changed, new-form, new-tier, layout-revised, new-program, gm-fix, none); --units, --check-declared; tests/tooling/test_review_owed.py 41 passed
- [x] T03 [US3] `scripts/_review_snapshot.py` per unit: the unit's map or sheet, the check's prompt with its `UNIT:` line; its tests (D4)
      research: rendering
      verify: DONE. DONE. _review_snapshot.py per unit: the unit's map or sheet both sides, a sheet owes no .json, the check's ASK with a UNIT: line, a unit not owed refused; 9 snapshot cases in test_review_owed.py
- [x] T04 [US6] `scripts/_review_prereq.py` per unit (`units_named`, sheets without a manifest, `--unit`); its tests
      research: rendering
      verify: DONE. DONE. _review_prereq.py: units_named (UNIT: lines, unanchored for a transcript's escaped JSON, and unit snapshot folders), unit_maps, stale_maps by the unit's map and snapshot, a sheet complete without .json, --unit; test_review_prereq.py 19 passed
- [x] T05 [US4] [US6] `pair-hooks.sh`: the five checks, one unit per dispatch, a GREEN gate, two rounds per unit per feature; `test-pair-hooks.sh` cases rewritten, each new branch proved by deleting it and watching a case go red (E1, E2, E4)
      research: rendering
      verify: DONE. DONE. pair-hooks.sh: five review agents, one unit per dispatch, gate_green (the stamp alone), round_number/record_round with REVIEW_ROUNDS_OK; test-pair-hooks 103 passed; mutation proof on a scratch copy: no round cap -> 4 red, a running gate accepted -> 2 red, settlement-review only -> 7 red
- [x] T06 [US3] `review-gate.sh`: owed units ship on their verdicts, an undeclared delta is refused, the notes-touch fallback and the rendering waiver gone; `test-review-gate.sh` cases (E3, E4)
      research: rendering
      verify: DONE. DONE. review-gate.sh: owed units ship on PASS/NEEDS-WORK at the pushed key, --check-declared refusal, notes-touch fallback and rendering waiver gone; test-review-gate 27 passed; mutation: declaration check removed -> 1 red, unit loop removed -> 5 red; make hooks-test 32 suites green
- [x] T07 `make verify` names the owed units and the undeclared delta; `make review-verdict UNIT=` (D4)
      research: rendering
      verify: DONE. DONE. make verify prints OCCASIONS NOT DECLARED and the owed units, writes per-unit prompts, says dispatch when green; make review-verdict UNIT= (MAP= kept as the same field)
- [x] T08 [US3] [US4] [US6] The replays (F): an engine change moving five manifests with `none:` owes zero units (SC-001); one new ink class, a declared redraw, a declared re-placement (the tannery, seeded) and a new element reusing an existing mark each owe exactly one glyph check (SC-002); a red gate and a missing record refuse a dispatch (SC-005)
      research: rendering
      verify: DONE. DONE. SC-001 test_an_engine_change_moving_every_manifest_owes_nothing; SC-002 test_an_element_new_to_a_map..., test_a_new_element_with_an_existing_mark..., test_a_declared_redraw..., test_a_declared_re_placement... (tannery); SC-005 test-pair-hooks section 12 (running-not-green refused) and 8b (unverified finding refused) and test-review-gate (NOT-REVIEWABLE refused)

## The contracts (C)

- [x] T09 [US1] [US4] `.claude/agents/glyph-check.md` (new; Opus high; `omitClaudeMd`): the element-in-place check, carrying the audit's C1, B29, C2a residual, C2c, C2e, C5, C6a, C6b funerary, C7, C9c rows and the shared process rows
      research: rendering
      verify: DONE. DONE. .claude/agents/glyph-check.md (7,666 chars; Opus high; omitClaudeMd): occasion, first stage, the element's reads/confusability/form/setting (cover, nuisance axis, funerary, traffic objective, pixel count), convention vs defect, output and verdict by UNIT; carries R1 C1, B29, C2a residual, C2c, C2e, C5, C6a, C6b funerary, C7, C9c
- [x] T10 [US1] `.claude/agents/fix-check.md` (new): the GM-complaint fix verification (S17, S7 adequacy, X1)
      research: rendering
      verify: DONE. DONE. .claude/agents/fix-check.md (3,609 chars): the GM's question at fit zoom first, the pixel count, did the fix fire (before/after), can the record bear it (the canopy case), verdict by UNIT; R1 S17, S7, X1
- [x] T11 [US1] [US5] `settlement-review.md` cut to the whole-map residue (C8, C6d, place, C2b/C2d on a new tier); every struck and cut row removed, the "gate can see / you must see" table rewritten; size before and after recorded (SC-004)
      research: rendering
      verify: DONE. DONE. settlement-review.md 49,960 -> 5,596 chars (wc -c, SC-004 at most half): twin detector, declared economy, first impression, fabric and the tier obligations on a new tier; every struck/cut row gone, its home named in the When section
- [x] T12 [US1] [US5] `building-review.md` cut to layout, program and coherence by occasion (with the merged dead-space sweeps); `size-audit.md` cut to anchors and voids
      research: rendering
      verify: DONE. DONE. building-review.md 31,033 -> 9,733 (circulation, privy/cesspit siting, realistic, dead space merged with pack-audit vacancies and backing voids, interior, plausibility; program on new-program; coherence on a new sheet); size-audit.md 23,471 -> 5,811 (anchors and the band to record, on a new kind or program)
- [x] T13 The tier table rows and `omitClaudeMd` for the two new agents (`test_agent_models.py`), their pre-authorization (`container-scripts/append-system-prompt.md`), and the struck tier-only obligations (outcast and status zoning, the border rule, the Imperial-road caption) in `migration-plan.md`'s town and city rows
      research: rendering
      verify: DONE. DONE. test_agent_models.py TIERS + glyph-check, fix-check (opus, high), 8 passed; append-system-prompt.md names both; migration-plan.md: outcast geography, status zoning, the border rule, the Imperial-road caption as tier placement rules, checked by the new-tier whole-map review

## The rules: Mode B (B1-B15)

- [x] T14 [US2] B1 record against ink (`tests/gate/`): channels on drawn water, gates and weirs on water, no house on a marsh; Kuwabata's supply run measured; red on a seeded fault first
      research: rendering
      verify: DONE. DONE. tests/gate/test_review_rules_294.py record_off_ink (channels within 3 ft of drawn water, sluice gates/weirs within 2 ft, no house on a marsh), seeded red (a 20 ft jog, a gate 7 ft off, a house on a marsh); Kuwabata's feed record ran 101 ft off its stub - fixed in comb.py (feed_stub, unit tests), 0 ft; green on the five
- [ ] T15 [US2] B2 ruled and plumb edges on the visible marsh, grove and clearing edges, from the page's id map; red on the recorded case or a seeded fault
      research: rendering
- [x] T16 [US2] B3 wood shed seating: a placer assert and a gate test
      research: rendering
      verify: DONE. DONE. shed_faults: nearer another household's house than its own, or turned off its rake (a quarter turn the same); seeded red (a neighbor's gable, a 45 deg turn); green on the five (the end-on/off-wall forms retired with the eaves woodpile, feature 280)
- [x] T17 [US2] B4's research pass: the branch spacing of a comb (kushi) irrigation layout
      research: physical
      - [x] research pass
      - [x] source-reader confirmed
      - [x] recorded and cited
      - [x] quote-check confirmed
      - [x] source-applicability confirmed
      verify: DONE. DONE. research pass: Japanese and English searches (an agent, 2026-10-01) - no premodern branch spacing; modern standards space by the block served; side-by-side supply/drain is Meiji-and-after; source-reader: no new source cited - the rule rests on water/030 and fields/070, already cited (tagoshi the old form); recorded: research/water/670 with its absence note and GUESS label; quote-check: no new footnote; source-applicability: no new or changed write-up; record-format: 0 vocabulary, 2 session notes applied
- [x] T18 [US2] B4 the twin-watercourse rule, comb branches included (T17's spacing enforced if found); red on the recorded case; the placer fixed on Inashiro, then the pool
      research: rendering
      verify: DONE. DONE. waterfields/twins.py (twin_run_ft, twins, drop_twin_deliveries) asked by comb._comb_canal_pieces and by sink.route_refusals/join_beside; unit tests red-first on a 20 ft twin; the four comb twins (190-310 ft) and Kashikawa's drain beside the brook (130 ft) gone; the gate rule green on the five
- [ ] T19 [US2] B5 see-through marks with their declared reasons; B5b crown species on the record and the conifer drawn above a broadleaf it overlaps; red first; the renderer's order fixed
      research: rendering
- [x] T20 [US2] B6 page hit regions (each class wins 0.8 of its ink, declared overlaps apart); red today; the hit order fixed
      research: rendering
      verify: DONE. DONE. tools/hit_share.py (visible-ink map vs id map; 3 unit tests, seeded a region polygon over another class's ink: 40%, thief named); gencache files the skip-render vector page as <map>.vector.html (page_of; test_gencache 23 passed); hit_thefts gate rule (80%, HIT_WIDEN's boxes declared), green on the five - measured with the visible-ink form the scout's storage-shed and mulberry-dike cases do not recur (paddy/bund/wet paddy lose only to declared widened boxes)
- [x] T21 [US2] B7 lane tread to wall, 4 ft: the tread rule and a gate test, red on the 3.85 ft case
      research: rendering
      verify: DONE. DONE. settlement/houses.py TREAD_WALL_FT = 4.0 (GUESS, research's 3-shaku eaves strip plus eaves; recorded case 3.85 ft) in _house_on_a_tread; treads_near_walls gate rule (raked house rects, STRtree), seeded red on the 3.85 ft case; the five regenerated and green
- [x] T22 [US2] B8 footbridges, B11 house bearings, B12 the brook in view, B13 the lane law on the shipped maps: gate tests, each red on a seeded fault
      research: rendering
      verify: DONE. DONE. bridges_too_close (60 ft, STRtree), bearing_faults (+-33.75 deg, no pile of 3+ at the widest turn), brook_pieces_in_view (one piece), law.needle_ends/needle_loops/lanes_that_kink on the shipped lanes; each seeded red; green on the five
- [x] T23 [US2] B9 drawn against rolled (15% of the rolled value): whether the record makes the roll a ceiling read first; red on Sawada's wood; the placer fixed
      research: rendering
      verify: DONE. DONE. research/vegetation/210 read: the register's RANGE is the rule, the per-homestead roll calibrated liberty, not a ceiling - so the placer was fixed: wood_goal.py rolls within the attainable part of the range, the copse filled to capacity and trimmed back; drawn/rolled Sawada 1.00, Inashiro 1.00, Kuwabata 1.001; drawn_off_roll gate rule (15%), seeded red on Sawada's 60%
- [x] T24 [US2] B10 declared forms drawn (fixture targets and minimums): red on Kuwabata; the fixture placer fixed on Kuwabata, then the pool
      research: rendering
      verify: DONE. DONE. undrawn_rolls (fixture targets and floors, byres, retirement houses, settlement form); Kuwabata red (3 households seated bare) - fixed in rolling/fit.py (_parts_fit refuses an unlaid layout), every target drawn on the five; unit test
- [ ] T25 [US2] B14 notes counts outside the census block and the dated history (the 55 found triaged), B15 every map folder has a notes file
      research: rendering

## The rules: Mode A (B15b-B24)

- [ ] T26 [US2] Registry checks B16 lodging entrances, B17 privies by zone (`compound.py` fixed for `ochiba-roundtrip-test`), B18 fire water, B19 size hierarchy, B20 sheet furniture - each with its red fixture and its tier entry
      research: rendering
- [ ] T27 [US2] B21 roads leave the frame, B22 palette roles, B23 gate feeds its road; the hand-drawn sheets they fail put to the GM in one message through `escalation-check` (D8)
      research: rendering
- [ ] T28 [US2] [US5] B24 `mapmatch`: gate side and width, roads under every key, the `**On map**` line required where a map records the sheet's subject
      research: rendering
- [ ] T29 [US2] B15b a sheet's notes counts against its `data-kind` census; B15c the size table covers every tagged kind
      research: rendering

## The ledger (G, A2)

- [ ] T30 [US7] `scripts/_review_cost.py` and `make review-cost AGENT=<id>`: a finished agent's wall time and tokens from its transcript; tests
      research: rendering
- [ ] T31 [US7] The ledger's new table; `scripts/_ledger_lint.py`; the `ledger-hooks.sh` guard on a commit staging the ledger, with its companion `test-ledger-hooks.sh` and its settings entry
      research: rendering
- [ ] T32 [US7] `docs/review-ledger-r0.json` (the old rows classified once, by an Opus agent) and `make review-census`; within R0's error (SC-006)
      research: rendering

## The documents (H)

- [ ] T33 [US9] The root `CLAUDE.md`, `dev/reviews.md`, `docs/spec-kit-and-reviews.md`, `docs/guards.md`, the constitution's per-map lines, the plan template's VI line, `SKILL.md`, the memory note; `make stale-terms F=294` clean
      research: rendering

## The tier (I)

- [ ] T34 [US8] The seeded tier experiment per check, three runs a leg, Sonnet against Opus; the tier table changed only where every Sonnet run finds the seeded finding
      research: rendering

## Landing

- [ ] T35 `make done` green; the owed units this delta's occasions name, dispatched on green and recorded in the ledger's new table; `294-end` and `make perf-report AGAINST=294-start`; the five LEGITIMATE narrowings put to the GM through `escalation-check`; land
      research: rendering
