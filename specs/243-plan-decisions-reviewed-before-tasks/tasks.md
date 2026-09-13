# Feature 243 - tasks

Spec FAITHFUL at round 3 (2026-09-13). Every task is `research: rendering`: this feature is tooling about
how a plan is reviewed, not about how a place was built. Every task that writes prose or code: American
spellings, hyphens only. No task is ticked before the gate and this plan's record exist (plan P8).

## A. The review comes first (FR-002, FR-009, FR-010)

- [ ] T01 `spec-fidelity` PLAN REVIEW of plan.md, recorded with
      `make plan-verdict F=243 FILE=<json> AS=spec-fidelity` (the subagent runs it)
      research: rendering
      verify:

## B. The gate (FR-001, FR-003 to FR-008)

- [ ] T02 `scripts/_plan_gate.py`: `owed`, `ticked`, `derive_verdict`, `record`, `touched_features`,
      `push_owed`, `tick_permitted`, `resolve` and the CLI (plan P1 to P6).
      research: rendering
      verify:
- [ ] T03 `scripts/tick-task.py` asks `tick_permitted` before a tick; the `tick` target exports
      `PLAN_REVIEW_OK` (FR-001, FR-005, FR-008).
      research: rendering
      verify:
- [ ] T04 `scripts/plan-gate.sh` run by `sync-with-main.sh` directly after `review-gate.sh`, escape first,
      recorded to the guard log and `dev/bypass-log/` (FR-007, FR-008).
      research: rendering
      verify:
- [ ] T05 `make plan-verdict` declines without `AS=spec-fidelity` and writes the record with it (FR-006).
      research: rendering
      verify:

## C. The documents (FR-009, FR-010)

- [ ] T06 `.claude/agents/spec-fidelity.md` MODE 4: PLAN REVIEW (FR-009).
      research: rendering
      verify:
- [ ] T07 `.specify/templates/tasks-template.md`: the plan review is the first task (FR-010).
      research: rendering
      verify:
- [ ] T08 `PLAN_REVIEW_OK` classified in the escape census; a row in the root `CLAUDE.md` guard table;
      `make docs` for the new target.
      research: rendering
      verify:

## D. Proven (SC-001 to SC-009)

- [ ] T09 `tests/tooling/test_plan_gate.py`, `scripts/test-plan-gate.sh` and the updated
      `test_tick_task.py`; every refusal broken in place and watched go red, then restored (SC-008).
      research: rendering
      verify:
- [ ] T10 `make hooks-test`, `make quick` and `make done` green; every tick of this feature made through
      the gate after T01's record (SC-009).
      research: rendering
      verify:
