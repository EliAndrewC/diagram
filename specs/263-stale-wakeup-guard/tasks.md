# Tasks - feature 263, a wakeup cannot outlive its purpose

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D6). Research: [`research.md`](research.md) (R1-R3).

**No task here is `research: physical`.** The feature is tooling; nothing is asserted about the world.

- [x] T01 Measure the Stop payload's cron shape with one wakeup and one reminder (R1)
      research: rendering
      verify: DONE. DONE. research.md R1: a CronCreate reminder and a ScheduleWakeup pending at turn end are both {id, schedule, recurring, prompt}; the transcript tells them apart.
- [x] T02 Measure a live /loop - invocation, wakeup prompt, stop - and the host's history (R3)
      research: rendering
      verify: DONE. DONE. research.md R3: 123 transcripts call ScheduleWakeup, none from /loop; a real loop measured - Skill invocation, /loop command entry on firing, wakeup prompt /loop <input>, stop:true.
- [x] T03 `scripts/wakeup-hooks.sh`: pretool and stop per FR-001-FR-005 (D1-D5)
      research: rendering
      verify: DONE. DONE. scripts/wakeup-hooks.sh: pretool refuses outside a live loop (fail closed), stop blocks every turn end naming CronDelete (fail open only on an unreadable transcript); no escape.
- [x] T04 `scripts/test-wakeup-hooks.sh`: every scenario of both stories, and each layer shown red with its rule deleted (FR-006)
      research: rendering
      verify: DONE. DONE. scripts/test-wakeup-hooks.sh 24 cases green; each layer shown red with its rule deleted (6 and 5 failing cases).
- [x] T05 Wiring and tables: `.claude/settings.json`, `CLAUDE.md`, `docs/guards.md` (FR-007, D6)
      research: rendering
      verify: DONE. DONE. .claude/settings.json (PreToolUse ScheduleWakeup + Stop), CLAUDE.md What-is-enforced row, docs/guards.md row.
- [x] T06 `make hooks-test` green, then land
      research: rendering
      verify: DONE. DONE. make hooks-test green (every suite).
