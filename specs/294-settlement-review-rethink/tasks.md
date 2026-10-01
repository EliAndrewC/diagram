# Tasks - feature 294, rethinking the settlement review

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (A-I, D1-D17; review CLEAR at round 3). Research: [`research.md`](research.md)
(R0-R3) and [`rules-recon.md`](rules-recon.md).
Order (plan): the trigger and the guards first, because every later engine task is verified under them; then the contracts;
then the rules, Mode B then Mode A, each engine fix on its reference artifact before the pool; then the ledger, the documents
and the tier experiment; then the landing.

## Occasions

This feature's own delta, declared under the rules it builds (plan D10). Lines are added as the rules land.

## Setup

- [x] T01 The baseline: `/tmp/base294` (detached worktree at the spec's HEAD) and the `294-start` bookend on unmodified code
      research: rendering
      verify: DONE. DONE. /tmp/base294 detached at 4a/HEAD before any edit; 294-start bookend on unmodified code: total 17.9 s, median 4.2 s, worst 5.8 s (dev/perf-log/20261001T151220Z-294-start-diagram-review.json)

## The trigger and the guards (D, E, F)

- [ ] T02 [US3] [US4] `scripts/_review_owed.py` answers occasions (detected: maps/sheets new to the pool, elements new to a map or sheet; declared: the `## Occasions` section), `--units`, `--check-declared`; `tests/tooling/test_review_owed.py` rewritten over git fixtures (D1-D3)
      research: rendering
- [ ] T03 [US3] `scripts/_review_snapshot.py` per unit: the unit's map or sheet, the check's prompt with its `UNIT:` line; its tests (D4)
      research: rendering
- [ ] T04 [US6] `scripts/_review_prereq.py` per unit (`units_named`, sheets without a manifest, `--unit`); its tests
      research: rendering
- [ ] T05 [US4] [US6] `pair-hooks.sh`: the five checks, one unit per dispatch, a GREEN gate, two rounds per unit per feature; `test-pair-hooks.sh` cases rewritten, each new branch proved by deleting it and watching a case go red (E1, E2, E4)
      research: rendering
- [ ] T06 [US3] `review-gate.sh`: owed units ship on their verdicts, an undeclared delta is refused, the notes-touch fallback and the rendering waiver gone; `test-review-gate.sh` cases (E3, E4)
      research: rendering
- [ ] T07 `make verify` names the owed units and the undeclared delta; `make review-verdict UNIT=` (D4)
      research: rendering
- [ ] T08 [US3] [US4] [US6] The replays (F): an engine change moving five manifests with `none:` owes zero units (SC-001); one new ink class, a declared redraw, a declared re-placement (the tannery, seeded) and a new element reusing an existing mark each owe exactly one glyph check (SC-002); a red gate and a missing record refuse a dispatch (SC-005)
      research: rendering

## The contracts (C)

- [ ] T09 [US1] [US4] `.claude/agents/glyph-check.md` (new; Opus high; `omitClaudeMd`): the element-in-place check, carrying the audit's C1, B29, C2a residual, C2c, C2e, C5, C6a, C6b funerary, C7, C9c rows and the shared process rows
      research: rendering
- [ ] T10 [US1] `.claude/agents/fix-check.md` (new): the GM-complaint fix verification (S17, S7 adequacy, X1)
      research: rendering
- [ ] T11 [US1] [US5] `settlement-review.md` cut to the whole-map residue (C8, C6d, place, C2b/C2d on a new tier); every struck and cut row removed, the "gate can see / you must see" table rewritten; size before and after recorded (SC-004)
      research: rendering
- [ ] T12 [US1] [US5] `building-review.md` cut to layout, program and coherence by occasion (with the merged dead-space sweeps); `size-audit.md` cut to anchors and voids
      research: rendering
- [ ] T13 The tier table rows and `omitClaudeMd` for the two new agents (`test_agent_models.py`), their pre-authorization (`container-scripts/append-system-prompt.md`), and the struck tier-only obligations (outcast and status zoning, the border rule, the Imperial-road caption) in `migration-plan.md`'s town and city rows
      research: rendering

## The rules: Mode B (B1-B15)

- [ ] T14 [US2] B1 record against ink (`tests/gate/`): channels on drawn water, gates and weirs on water, no house on a marsh; Kuwabata's supply run measured; red on a seeded fault first
      research: rendering
- [ ] T15 [US2] B2 ruled and plumb edges on the visible marsh, grove and clearing edges, from the page's id map; red on the recorded case or a seeded fault
      research: rendering
- [ ] T16 [US2] B3 wood shed seating: a placer assert and a gate test
      research: rendering
- [ ] T17 [US2] B4's research pass: the branch spacing of a comb (kushi) irrigation layout
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [ ] quote-check confirmed
      - [ ] source-applicability confirmed
- [ ] T18 [US2] B4 the twin-watercourse rule, comb branches included (T17's spacing enforced if found); red on the recorded case; the placer fixed on Inashiro, then the pool
      research: rendering
- [ ] T19 [US2] B5 see-through marks with their declared reasons; B5b crown species on the record and the conifer drawn above a broadleaf it overlaps; red first; the renderer's order fixed
      research: rendering
- [ ] T20 [US2] B6 page hit regions (each class wins 0.8 of its ink, declared overlaps apart); red today; the hit order fixed
      research: rendering
- [ ] T21 [US2] B7 lane tread to wall, 4 ft: the tread rule and a gate test, red on the 3.85 ft case
      research: rendering
- [ ] T22 [US2] B8 footbridges, B11 house bearings, B12 the brook in view, B13 the lane law on the shipped maps: gate tests, each red on a seeded fault
      research: rendering
- [ ] T23 [US2] B9 drawn against rolled (15% of the rolled value): whether the record makes the roll a ceiling read first; red on Sawada's wood; the placer fixed
      research: rendering
- [ ] T24 [US2] B10 declared forms drawn (fixture targets and minimums): red on Kuwabata; the fixture placer fixed on Kuwabata, then the pool
      research: rendering
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
