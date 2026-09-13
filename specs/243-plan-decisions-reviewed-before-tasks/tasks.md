# Feature 243 - tasks

Spec FAITHFUL at round 3 (2026-09-13). Every task is `research: rendering`: this feature is tooling about
how a plan is reviewed, not about how a place was built. Every task that writes prose or code: American
spellings, hyphens only. No task is ticked before the gate and this plan's record exist (plan P8).

## A. The review comes first (FR-002, FR-009, FR-010)

- [x] T01 `spec-fidelity` PLAN REVIEW of plan.md, recorded with
      `make plan-verdict F=243 FILE=<json> AS=spec-fidelity` (the subagent runs it)
      research: rendering
      verify: DONE. spec-fidelity MODE 4 on plan.md at 11a0440c: 12 decisions, all within, CLEAR; recorded by the subagent through make plan-verdict AS=spec-fidelity

## B. The gate (FR-001, FR-003 to FR-008)

- [x] T02 `scripts/_plan_gate.py`: `owed`, `ticked`, `derive_verdict`, `record`, `touched_features`,
      `push_owed`, `tick_permitted`, `resolve` and the CLI (plan P1 to P6).
      research: rendering
      verify: DONE. _plan_gate.py carries owed, ticked, derive_verdict, record, touched_features, push_owed, tick_permitted, resolve and the CLI; 12 module tests green
- [x] T03 `scripts/tick-task.py` asks `tick_permitted` before a tick; the `tick` target exports
      `PLAN_REVIEW_OK` (FR-001, FR-005, FR-008).
      research: rendering
      verify: DONE. tick-task.py asks tick_permitted before a tick; the tick target exports PLAN_REVIEW_OK; a refused tick writes nothing (test_plan_gate), and this very tick went through the gate
- [x] T04 `scripts/plan-gate.sh` run by `sync-with-main.sh` directly after `review-gate.sh`, escape first,
      recorded to the guard log and `dev/bypass-log/` (FR-007, FR-008).
      research: rendering
      verify: DONE. plan-gate.sh runs after review-gate.sh in sync-with-main.sh; test-plan-gate.sh 12 of 12; the sync suite now proves the wiring (48 checks, red when the call is removed)
- [x] T05 `make plan-verdict` declines without `AS=spec-fidelity` and writes the record with it (FR-006).
      research: rendering
      verify: DONE. make plan-verdict declined without AS (exit 2, nothing written) and recorded CLEAR with AS=spec-fidelity

## C. The documents (FR-009, FR-010)

- [x] T06 `.claude/agents/spec-fidelity.md` MODE 4: PLAN REVIEW (FR-009).
      research: rendering
      verify: DONE. spec-fidelity.md MODE 4: PLAN REVIEW - request verbatim, digest first, decisions found by the reviewer, classified and ruled, recorded by the target
- [x] T07 `.specify/templates/tasks-template.md`: the plan review is the first task (FR-010).
      research: rendering
      verify: DONE. tasks-template: the first-task rule with its shape, and T001 in the sample phase is the plan review
- [x] T08 `PLAN_REVIEW_OK` classified in the escape census; a row in the root `CLAUDE.md` guard table;
      `make docs` for the new target.
      research: rendering
      verify: DONE. PLAN_REVIEW_OK classified environment in the escape census (test green); guard-table row in CLAUDE.md; make docs wrote 68 targets, 0 undocumented

## D. Proven (SC-001 to SC-009)

- [x] T09 `tests/tooling/test_plan_gate.py`, `scripts/test-plan-gate.sh` and the updated
      `test_tick_task.py`; every refusal broken in place and watched go red, then restored (SC-008).
      research: rendering
      verify: DONE. 12 of 12 refusals red when broken and restored (scratchpad mutate243.py), plus the push wiring red in the sync suite; test_tick_task updated for the gate
- [x] T10 `make hooks-test`, `make quick` and `make done` green; every tick of this feature made through
      the gate after T01's record (SC-009).
      research: rendering
      verify: DONE. make hooks-test green (24 suites, 5 re-run), make quick green, make done green FULL scope 3870 passed with the coverage floors; T01-T10 each ticked through the gate after the CLEAR record
