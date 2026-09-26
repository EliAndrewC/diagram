# Tasks - feature 263, a wakeup cannot outlive its purpose

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D6). Research: [`research.md`](research.md) (R1-R3).

**No task here is `research: physical`.** The feature is tooling; nothing is asserted about the world.

- [ ] T01 Measure the Stop payload's cron shape with one wakeup and one reminder (R1)
      research: rendering
- [ ] T02 Measure a live /loop - invocation, wakeup prompt, stop - and the host's history (R3)
      research: rendering
- [ ] T03 `scripts/wakeup-hooks.sh`: pretool and stop per FR-001-FR-005 (D1-D5)
      research: rendering
- [ ] T04 `scripts/test-wakeup-hooks.sh`: every scenario of both stories, and each layer shown red with its rule deleted (FR-006)
      research: rendering
- [ ] T05 Wiring and tables: `.claude/settings.json`, `CLAUDE.md`, `docs/guards.md` (FR-007, D6)
      research: rendering
- [ ] T06 `make hooks-test` green, then land
      research: rendering
