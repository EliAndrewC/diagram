# Tasks - 249 review rounds read the diff, and the notice speaks on any single call

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling, nothing
physical behind it.

- [ ] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the plan
      reviewed (MODE 4) before any tick
      research: rendering
      verify:
- [ ] T02 the batching notice on any single call, and its suite case (FR-001)
      research: rendering
      verify:
- [ ] T03 `scripts/review-round-hooks.sh`: the rewrite, the first-round snapshot, the history-without-
      snapshot line, the no-feature pass, the escape (FR-002 to FR-004); wired in settings
      research: rendering
      verify:
- [ ] T04 `scripts/test-review-round-hooks.sh` and the census rows (FR-006); `make hooks-test` green
      research: rendering
      verify:
- [ ] T05 the agent contract (FR-005) and the record (FR-007); `make quick` green; land DIRECT (FR-008)
      research: rendering
      verify:
