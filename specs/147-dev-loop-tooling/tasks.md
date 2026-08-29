# Tasks: Dev-loop tooling - the probe, the audit, the profile, and the paired gate

**Feature**: 147-dev-loop-tooling | **30 tasks** | **Spec**: [spec.md](spec.md) (FAITHFUL) | **Plan**: [plan.md](plan.md)

Every task here is `research: procedure` - this feature draws nothing and states nothing about how a place
was built, so no task carries the three physical-research boxes (constitution v2.12.0; the classification
is enforced by `tests/test_task_research_boxes.py`).

**MVP**: US1 + US2 (the probe and the audit) - together they remove the two biggest measured costs, and
each is useful the moment it lands.

## Phase 1: Foundational (blocks the pairing only)

- [x] T001 Settle R1 - does a `PreToolUse` event fire for the Agent tool in this harness, and does its `tool_input` carry `subagent_type` and `prompt`? Register a temporary logging matcher in `.claude/settings.json`, dispatch a trivial agent, read what arrived, remove the matcher, and write the answer into `specs/147-dev-loop-tooling/research.md` R1 along with which enforcement point US3 will use (the Agent pretool, or the Stop-hook fallback).
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [x] T002 [P] Confirm the geometry helpers both new tools import (`l7r/diagram/settlement/_geom`: `seg_dist`, `seg_closest`, `point_in_poly`) are importable from a tool without dragging a Settlement into being, and note in `plan.md` Design if anything has to move. One implementation of each measure, never a second copy in a tool.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure

## Phase 2: User Story 1 - the polder probe (P1)

**Goal**: measure a polder geometry change in about a second, without drawing a map.
**Independent test**: change a polder rule, run the probe, read the metrics; no map is rendered.

- [x] T010 [US1] Write `l7r/diagram/tools/polder_probe.py` - build the block through `hamletgen.plan_site` + `hamletgen.fit_polder` (the same path `stage_polder` takes, so the probe cannot pass while the map fails) and print the metrics table from plan.md Design 1: parcels overlapping a channel with coordinates, minimum and median berm, acreage against target, per-parcel vertex count and square-corner mean, ring point counts, wall time. Carries the `_invocation.guard` entry-point refusal.
      given 2026-08-29T03:15Z | done 2026-08-29T03:45Z | elapsed ~30 min (US1 whole) | runs: 4 probe runs, 3 quick runs.
      research: procedure
- [x] T011 [US1] Exit non-zero when a metric would fail the gate - overlap > 0, any parcel under 12 vertices, square-corner mean over 2.5 - so the probe can guard an expensive run; print WHICH metric failed.
      given 2026-08-29T03:15Z | done 2026-08-29T03:45Z | elapsed ~30 min (US1 whole) | runs: 4 probe runs, 3 quick runs.
      research: procedure
- [x] T012 [US1] Add the `polder-probe` target to `.claude/skills/diagram/Makefile` (`SEED=`, `SEEDS=`, `ARCHETYPE=`), following the `$(RUN).tools.*` shape of `why-placed` and `crop`.
      given 2026-08-29T03:15Z | done 2026-08-29T03:45Z | elapsed ~30 min (US1 whole) | runs: 4 probe runs, 3 quick runs.
      research: procedure
- [x] T013 [US1] `tests/tools/test_polder_probe.py` - the metrics are right on a known block; a seeded violation exits non-zero and names the metric; and the probe's numbers AGREE with the same block's rolled manifest (the guard against the probe becoming a second implementation).
      given 2026-08-29T03:15Z | done 2026-08-29T03:45Z | elapsed ~30 min (US1 whole) | runs: 4 probe runs, 3 quick runs.
      research: procedure
- [x] T014 [US1] Measure the probe's wall time against SC-001 (about a second, at most three) and record the number in the skill's command map row.
      given 2026-08-29T03:15Z | done 2026-08-29T03:45Z | elapsed ~30 min (US1 whole) | runs: 4 probe runs, 3 quick runs. measured 0.23 s for one block (0.41 s wall through make), against SC-001's 'about a second, at most three' and the 47 s median map roll it replaces
      research: procedure

## Phase 3: User Story 2 - the overlap audit (P1)

**Goal**: ask "does A overlap B" with one command, over records and over drawn ink.
**Independent test**: the questions asked by hand in T50-T55 answered on the shipped maps, no script written.

- [x] T020 [US2] Write `l7r/diagram/tools/overlap_audit.py` with the RECORD families from plan.md Design 2 - `footprints-water`, `footprints-marsh`, `parcels-channels` - each naming its offenders with family, coordinates and count. Entry-point guard as above.
      given 2026-08-29T03:15Z | done 2026-08-29T04:30Z | elapsed ~45 min (US2 whole) | runs: 9 audit runs over 5 maps, 6 quick runs, 2 map rolls
      research: procedure
- [x] T021 [US2] Add the INK families - `ink-mounds`, `ink-water` - reading the rendered SVG beside the manifest, by each mark's own reach (a tint circle by its radius, a blade by its length). This is the half the manifest cannot answer and half the questions asked in T54/T55 needed.
      given 2026-08-29T03:15Z | done 2026-08-29T04:30Z | elapsed ~45 min (US2 whole) | runs: 9 audit runs over 5 maps, 6 quick runs, 2 map rolls
      research: procedure
- [x] T022 [US2] A family whose inputs a map does not carry reports `unmeasured`, never `0`; the tool exits non-zero only on a real offender.
      given 2026-08-29T03:15Z | done 2026-08-29T04:30Z | elapsed ~45 min (US2 whole) | runs: 9 audit runs over 5 maps, 6 quick runs, 2 map rolls
      research: procedure
- [x] T023 [US2] Add the `overlap-audit` target to the skill Makefile (`M=`, optional `FAMILIES=`).
      given 2026-08-29T03:15Z | done 2026-08-29T04:30Z | elapsed ~45 min (US2 whole) | runs: 9 audit runs over 5 maps, 6 quick runs, 2 map rolls
      research: procedure
- [x] T024 [US2] `tests/tools/test_overlap_audit.py` - each family fires on a hand-built offending manifest/SVG and stays silent on a clean one; `unmeasured` is reported rather than a zero.
      given 2026-08-29T03:15Z | done 2026-08-29T04:30Z | elapsed ~45 min (US2 whole) | runs: 9 audit runs over 5 maps, 6 quick runs, 2 map rolls
      research: procedure
- [ ] T025 [US2] SC-002 demonstration: re-ask on the shipped maps every overlap question T54 and T55 answered by hand (marsh ink on a mound, a footprint on marsh, a parcel across a ditch, a mark over water) using only this tool, and record the commands in `quickstart.md`.
      given 2026-08-29T03:15Z | done - | elapsed - | runs: -
      research: procedure

## Phase 4: User Story 3 - the paired gate and review (P2)

**Goal**: one command starts both; neither runs alone without an override that logs its reason.
**Independent test**: attempt each half alone and observe the refusal; run the pairing command and observe both start.

- [x] T030 [US3] Add the `verify` target to the skill Makefile: record the pairing intent for the current engine key, launch the gate detached, print the review dispatch line naming the maps whose manifests differ from HEAD.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [x] T031 [US3] Write `scripts/pair-hooks.sh` `pretool` for Bash: refuse a gate invocation unless a settlement-review is pending in this session, or a review record matches the current engine key, or the pairing token is fresh, or `PAIR_OK=<reason>` is present. Reuse `agent-watch-hooks.sh scan` for "pending"; key on `.git/verification-state.json`'s `engine_key`.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [x] T032 [US3] Enforce the other direction at the point T001 settled: refuse a `settlement-review` dispatch when no gate is running or freshly green for this engine key. Record in the script's header WHICH point is in force and why.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [x] T033 [US3] `pair-hooks.sh stop`: refuse ONCE to end a turn while a pairing is half-open - a gate went green on this engine key and no review was dispatched - in the shape `agent-watch-hooks.sh` already uses.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [x] T034 [US3] The override: one token, `PAIR_OK`, which must carry a reason, runs the command, and appends the reason to `dev/bypass-log/` in the existing record shape.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [ ] T035 [US3] The unattended case: `make idle-tests` supplies `PAIR_OK` with its fixed reason ("idle run: no session attached to dispatch a review") so the audit line exists. NOT an exemption in the guard - an exemption is the shape spec-fidelity struck from the spec.
      given 2026-08-29T03:15Z | done - | elapsed - | runs: -
      research: procedure
- [x] T036 [US3] Register the hooks in `.claude/settings.json` (PreToolUse for Bash and, per T001, for the Agent tool; Stop) alongside the existing entries.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [x] T037 [US3] `scripts/test-pair-hooks.sh` - each refusal fires; each allowance passes (review pending, record fresh, pairing token fresh, override); the Stop refusal fires once and only once; and a MENTION of the guarded commands inside a heredoc or a quoted string is NOT blocked (the shape that blocked this feature's own time audit three times). Wire it into `make hooks-test`.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [x] T038 [US3] Prove the guard fires by deleting it and watching a test go red (CLAUDE.md's third property for a new guard), and record that in the test's docstring.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure

## Phase 5: User Story 4 - per-stage timings (P3)

- [x] T040 [US4] Time each stage in `hamletgen/driver.py` `build()` when `L7R_STAGE_PROFILE` is set; print the per-stage table, the total and the slowest stage. With the variable unset the loop is exactly today's.
      given 2026-08-29T03:15Z | done 2026-08-29T04:45Z | elapsed ~15 min (US4 whole) | runs: 3 profiled rolls, 3 quick runs. First profile on Kuwabata: 33.7 s total, stage_hinterland 13.9 s (41%), stage_waterward 9.5 s (28%)
      research: procedure
- [x] T041 [US4] Plumb `PROFILE=1` through the skill Makefile's `map` and `hamlet` targets, and record at the point of change why an environment variable is legitimate here where feature 132 forbids one for switches (it changes what is PRINTED, never what is ROLLED).
      given 2026-08-29T03:15Z | done 2026-08-29T04:45Z | elapsed ~15 min (US4 whole) | runs: 3 profiled rolls, 3 quick runs. First profile on Kuwabata: 33.7 s total, stage_hinterland 13.9 s (41%), stage_waterward 9.5 s (28%)
      research: procedure
- [x] T042 [US4] Test: the manifest of a rolled map is byte-identical with the flag on and off, and the table appears only when it is on.
      given 2026-08-29T03:15Z | done 2026-08-29T04:45Z | elapsed ~15 min (US4 whole) | runs: 3 profiled rolls, 3 quick runs. First profile on Kuwabata: 33.7 s total, stage_hinterland 13.9 s (41%), stage_waterward 9.5 s (28%)
      research: procedure

## Phase 6: Polish and cross-cutting

- [x] T050 [P] Two rows in `l7r/diagram/tools/CLAUDE.md`'s "You are asking / Reach for" table, phrased as the questions these tools answer.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [x] T051 [P] Rows in the skill `CLAUDE.md` command map with MEASURED times (never estimates), and a line in the always-on section pointing the geometry loop at the probe rather than at a map roll.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [x] T052 [P] A row in the root `CLAUDE.md` "WHAT IS ENFORCED, AND WHERE" table for the pairing guard, with its override and its test companion.
      given 2026-08-29T03:15Z | done 2026-08-29T05:20Z | elapsed ~50 min (US3 whole) | runs: 6 guard-suite runs, 1 hooks-test
      research: procedure
- [ ] T053 Verification pass: the reference hamlet's and Kuwabata's manifests byte-identical to their pre-feature rolls; lint, types, the quick suite; one gate run; `make hooks-test` green.
      given 2026-08-29T03:15Z | done - | elapsed - | runs: -
      research: procedure
- [ ] T054 Record the feature's own numbers where the next session will find them: the probe's measured time, the audit's families, and the pairing's enforcement point, in `dev/loop.md` beside the rest of the dev-loop doctrine.
      given 2026-08-29T03:15Z | done - | elapsed - | runs: -
      research: procedure

## Dependencies

- T001 blocks T032 and T036 (it decides where the second half is enforced). Nothing else waits on it.
- US1, US2 and US4 are independent of each other and of US3; any of them can land alone.
- T053 runs last, after every other task, and is the only task that may not be parallelized.
